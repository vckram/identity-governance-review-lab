from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schema import SCHEMAS, FieldSpec
from .types import ParseError, parse_value


@dataclass(frozen=True)
class TableResult:
    name: str
    path: Path
    rows: list[dict[str, Any]]
    errors: list[str]

    @property
    def record_count(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class DatasetResult:
    tables: dict[str, TableResult]

    @property
    def table_names(self) -> list[str]:
        return list(self.tables)

    @property
    def total_records(self) -> int:
        return sum(table.record_count for table in self.tables.values())

    @property
    def total_errors(self) -> int:
        return sum(len(table.errors) for table in self.tables.values())


def load_dataset(data_dir: Path) -> DatasetResult:
    tables = {
        table_name: load_table(data_dir / schema.file_name, table_name, schema.fields)
        for table_name, schema in SCHEMAS.items()
    }
    return DatasetResult(tables=tables)


def load_table(path: Path, table_name: str, fields: tuple[FieldSpec, ...]) -> TableResult:
    errors: list[str] = []
    rows: list[dict[str, Any]] = []

    if not path.exists():
        return TableResult(
            name=table_name,
            path=path,
            rows=[],
            errors=[f"{path}: file is missing"],
        )

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                return TableResult(
                    name=table_name,
                    path=path,
                    rows=[],
                    errors=[f"{path}: file has no header row"],
                )

            header_errors = validate_header(path, reader.fieldnames, fields)
            errors.extend(header_errors)

            for line_number, raw_row in enumerate(reader, start=2):
                parsed_row: dict[str, Any] = {}
                for field in fields:
                    raw_value = raw_row.get(field.name, "")
                    try:
                        parsed_row[field.name] = parse_field(field, raw_value)
                    except ParseError as exc:
                        errors.append(f"{path}:{line_number}: {field.name}: {exc}")
                        parsed_row[field.name] = None
                rows.append(parsed_row)
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        errors.append(f"{path}: could not read or parse file: {exc}")

    return TableResult(name=table_name, path=path, rows=rows, errors=errors)


def validate_header(path: Path, fieldnames: list[str], fields: tuple[FieldSpec, ...]) -> list[str]:
    expected = {field.name for field in fields}
    actual = set(fieldnames)
    errors = []

    for missing in sorted(expected - actual):
        errors.append(f"{path}: missing expected column {missing}")

    for unexpected in sorted(actual - expected):
        errors.append(f"{path}: unexpected column {unexpected}")

    return errors


def parse_field(field: FieldSpec, raw_value: str | None) -> Any:
    if raw_value is None or raw_value.strip() == "":
        if field.required:
            raise ParseError("required field is blank")
        return None

    parsed_value = parse_value(raw_value.strip(), field.field_type)
    if field.allowed_values is not None and parsed_value not in field.allowed_values:
        allowed_values = ", ".join(field.allowed_values)
        raise ParseError(f"expected one of: {allowed_values}")

    return parsed_value
