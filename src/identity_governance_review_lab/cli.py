from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load sample identity governance CSV files and print a validation summary."
    )
    parser.add_argument(
        "--data-dir",
        default="sample-data",
        help="Directory containing the synthetic CSV files. Defaults to sample-data.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_dir = Path(args.data_dir)
    dataset = load_dataset(data_dir)

    print("Identity Governance Review Lab validation summary")
    print(f"Data directory: {data_dir}")
    print()

    for table_name in dataset.table_names:
        table = dataset.tables[table_name]
        print(f"- {table_name}: {table.record_count} record(s), {len(table.errors)} validation error(s)")
        for error in table.errors:
            print(f"  - {error}")

    print()
    print(f"Total records: {dataset.total_records}")
    print(f"Total validation errors: {dataset.total_errors}")

    return 1 if dataset.total_errors else 0
