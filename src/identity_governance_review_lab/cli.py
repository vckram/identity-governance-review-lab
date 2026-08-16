from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_dataset
from .rules import Finding, find_terminated_enabled_accounts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load sample identity governance CSV files and print a validation summary."
    )
    parser.add_argument(
        "--data-dir",
        default="sample-data",
        help="Directory containing the synthetic CSV files. Defaults to sample-data.",
    )
    parser.add_argument(
        "--r1",
        action="store_true",
        help="After validation, print R1_TERMINATED_ENABLED_ACCOUNT findings only.",
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

    if dataset.total_errors:
        if args.r1:
            print()
            print("R1 findings were not evaluated because validation errors were found.")
        return 1

    if args.r1:
        print()
        print_r1_findings(find_terminated_enabled_accounts(dataset))

    return 0


def print_r1_findings(findings: list[Finding]) -> None:
    print("R1_TERMINATED_ENABLED_ACCOUNT findings")
    print("These findings are discrepancies requiring human review, not automatic danger.")
    print()

    if not findings:
        print("No R1 findings.")
        return

    for index, finding in enumerate(findings, start=1):
        print(f"{index}. {finding.description}")
        print(f"   Severity: {finding.severity}")
        print(f"   Review: {finding.review_guidance}")
        print("   Evidence:")
        for key, value in finding.evidence.items():
            print(f"   - {key}: {value}")
