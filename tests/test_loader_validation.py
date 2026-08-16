from __future__ import annotations

from pathlib import Path

from identity_governance_review_lab.loader import load_table
from identity_governance_review_lab.schema import SCHEMAS


def write_csv(path: Path, header: list[str], row: list[str]) -> None:
    path.write_text(",".join(header) + "\n" + ",".join(row) + "\n", encoding="utf-8")


def load_single_table(tmp_path: Path, table_name: str, header: list[str], row: list[str]):
    schema = SCHEMAS[table_name]
    csv_path = tmp_path / schema.file_name
    write_csv(csv_path, header, row)

    return load_table(csv_path, table_name, schema.fields)


def test_missing_required_column_produces_validation_error(tmp_path: Path) -> None:
    result = load_single_table(
        tmp_path,
        "hr_workers",
        [
            "worker_display_name",
            "worker_type",
            "worker_status",
            "employment_start_date",
            "termination_date",
            "contract_end_date",
            "department",
            "manager_worker_key",
            "hr_record_last_updated",
        ],
        [
            "Avery Stone",
            "employee",
            "active",
            "2024-01-15",
            "",
            "",
            "IT",
            "wrk-001",
            "2026-08-01",
        ],
    )

    assert any("missing expected column worker_key" in error for error in result.errors)


def test_unexpected_column_produces_validation_error(tmp_path: Path) -> None:
    result = load_single_table(
        tmp_path,
        "groups",
        [
            "group_id",
            "display_name",
            "description",
            "group_type",
            "is_privileged_group",
            "owner_worker_key",
            "access_justification",
            "extra_column",
        ],
        [
            "grp-001",
            "Helpdesk Operators",
            "Synthetic group",
            "security",
            "false",
            "wrk-001",
            "Access review lab sample",
            "unexpected",
        ],
    )

    assert any("unexpected column extra_column" in error for error in result.errors)


def test_invalid_boolean_value_produces_validation_error(tmp_path: Path) -> None:
    result = load_single_table(
        tmp_path,
        "entra_users",
        [
            "entra_user_id",
            "worker_key",
            "user_principal_name",
            "display_name",
            "account_enabled",
            "user_type",
            "created_date",
            "last_sign_in_date",
            "department",
            "manager_worker_key",
            "account_owner_worker_key",
            "account_justification",
            "review_notes",
            "days_since_last_sign_in",
            "dormancy_review_status",
        ],
        [
            "usr-001",
            "wrk-001",
            "avery.stone@example.invalid",
            "Avery Stone",
            "yes",
            "employee",
            "2024-01-15",
            "2026-08-01",
            "IT",
            "wrk-002",
            "wrk-002",
            "Standard account",
            "",
            "15",
            "clean",
        ],
    )

    assert any("account_enabled: expected boolean value true or false" in error for error in result.errors)


def test_invalid_date_value_produces_validation_error(tmp_path: Path) -> None:
    result = load_single_table(
        tmp_path,
        "hr_workers",
        [
            "worker_key",
            "worker_display_name",
            "worker_type",
            "worker_status",
            "employment_start_date",
            "termination_date",
            "contract_end_date",
            "department",
            "manager_worker_key",
            "hr_record_last_updated",
        ],
        [
            "wrk-001",
            "Avery Stone",
            "employee",
            "active",
            "not-a-date",
            "",
            "",
            "IT",
            "wrk-002",
            "2026-08-01",
        ],
    )

    assert any("employment_start_date: expected ISO date in YYYY-MM-DD format" in error for error in result.errors)


def test_invalid_enum_value_produces_validation_error(tmp_path: Path) -> None:
    result = load_single_table(
        tmp_path,
        "hr_workers",
        [
            "worker_key",
            "worker_display_name",
            "worker_type",
            "worker_status",
            "employment_start_date",
            "termination_date",
            "contract_end_date",
            "department",
            "manager_worker_key",
            "hr_record_last_updated",
        ],
        [
            "wrk-001",
            "Avery Stone",
            "full-time",
            "active",
            "2024-01-15",
            "",
            "",
            "IT",
            "wrk-002",
            "2026-08-01",
        ],
    )

    assert any("worker_type: expected one of: employee, contractor" in error for error in result.errors)


def test_invalid_registered_methods_json_produces_validation_error(tmp_path: Path) -> None:
    result = load_single_table(
        tmp_path,
        "mfa_registration",
        [
            "mfa_record_id",
            "entra_user_id",
            "has_mfa_capable_method",
            "registered_methods",
            "default_method",
            "registration_last_updated",
            "mfa_registration_evidence",
        ],
        [
            "mfa-001",
            "usr-001",
            "true",
            "not-json",
            "Microsoft Authenticator",
            "2026-08-01",
            "Synthetic evidence",
        ],
    )

    assert any("registered_methods: expected JSON list of strings" in error for error in result.errors)


def test_unreadable_csv_input_is_validation_error_instead_of_crashing(tmp_path: Path) -> None:
    schema = SCHEMAS["hr_workers"]
    csv_path = tmp_path / schema.file_name
    csv_path.write_bytes(b"\xff\xfe\x00")

    result = load_table(csv_path, "hr_workers", schema.fields)

    assert result.rows == []
    assert any("could not read or parse file" in error for error in result.errors)
