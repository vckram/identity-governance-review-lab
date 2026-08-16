from __future__ import annotations

import json
from datetime import date
from typing import Any


class ParseError(ValueError):
    """Raised when a CSV value cannot be parsed into the normalized schema type."""


def parse_value(raw_value: str, field_type: str) -> Any:
    if field_type in {"string", "string_enum"}:
        return raw_value
    if field_type == "string_or_null":
        return parse_nullable_string(raw_value)
    if field_type == "boolean":
        return parse_boolean(raw_value)
    if field_type == "boolean_or_null":
        return parse_nullable(raw_value, parse_boolean)
    if field_type == "date":
        return parse_date(raw_value)
    if field_type == "date_or_null":
        return parse_nullable(raw_value, parse_date)
    if field_type == "integer_or_null":
        return parse_nullable(raw_value, parse_integer)
    if field_type == "list_of_strings":
        return parse_string_list(raw_value)
    raise ParseError(f"unknown field type {field_type!r}")


def parse_nullable(raw_value: str, parser: Any) -> Any:
    if raw_value.lower() == "null":
        return None
    return parser(raw_value)


def parse_nullable_string(raw_value: str) -> str | None:
    if raw_value.lower() == "null":
        return None
    return raw_value


def parse_boolean(raw_value: str) -> bool:
    normalized = raw_value.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ParseError("expected boolean value true or false")


def parse_date(raw_value: str) -> date:
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ParseError("expected ISO date in YYYY-MM-DD format") from exc


def parse_integer(raw_value: str) -> int:
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ParseError("expected integer") from exc


def parse_string_list(raw_value: str) -> list[str]:
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ParseError("expected JSON list of strings") from exc

    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ParseError("expected JSON list of strings")

    return parsed
