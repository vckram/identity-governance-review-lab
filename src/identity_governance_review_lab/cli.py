from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_dataset
from .rules import (
    Finding,
    find_contractors_active_past_end_date,
    find_terminated_enabled_accounts,
    find_terminated_privileged_access,
)


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
    parser.add_argument(
        "--r2",
        action="store_true",
        help="After validation, print R2_TERMINATED_PRIVILEGED_ACCESS findings only.",
    )
    parser.add_argument(
        "--r3",
        action="store_true",
        help="After validation, print R3_CONTRACTOR_ACTIVE_PAST_END_DATE findings only.",
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
        if args.r1 or args.r2 or args.r3:
            print()
            print("Rule findings were not evaluated because validation errors were found.")
        return 1

    if args.r1:
        print()
        print_findings(
            "R1_TERMINATED_ENABLED_ACCOUNT",
            find_terminated_enabled_accounts(dataset),
        )

    if args.r2:
        print()
        print_findings(
            "R2_TERMINATED_PRIVILEGED_ACCESS",
            find_terminated_privileged_access(dataset),
        )

    if args.r3:
        print()
        print_findings(
            "R3_CONTRACTOR_ACTIVE_PAST_END_DATE",
            find_contractors_active_past_end_date(dataset),
        )

    return 0


def print_findings(rule_id: str, findings: list[Finding]) -> None:
    print(f"{rule_id} findings")
    print("These findings are discrepancies requiring human review, not automatic danger.")
    print()

    if not findings:
        print(f"No {rule_id} findings.")
        return

    for index, finding in enumerate(findings, start=1):
        print(f"{index}. {finding.description}")
        print(f"   Severity: {finding.severity}")
        print(f"   Review: {finding.review_guidance}")
        print("   Evidence:")
        for key, value in finding.evidence.items():
            print(f"   - {key}: {value}")
