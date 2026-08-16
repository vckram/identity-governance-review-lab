from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from identity_governance_review_lab.loader import DatasetResult, TableResult
from identity_governance_review_lab.rules import (
    find_privileged_missing_owner_or_justification,
    find_terminated_privileged_access,
    review_dormant_enabled_accounts,
    review_mfa_capable_registration,
)


def make_dataset(
    *,
    hr_workers: list[dict[str, Any]] | None = None,
    entra_users: list[dict[str, Any]] | None = None,
    privileged_role_assignments: list[dict[str, Any]] | None = None,
    mfa_registration: list[dict[str, Any]] | None = None,
) -> DatasetResult:
    rows_by_table = {
        "hr_workers": hr_workers or [],
        "entra_users": entra_users or [],
        "groups": [],
        "group_memberships": [],
        "privileged_role_assignments": privileged_role_assignments or [],
        "mfa_registration": mfa_registration or [],
    }
    return DatasetResult(
        tables={
            table_name: TableResult(
                name=table_name,
                path=Path(f"<memory>/{table_name}.csv"),
                rows=rows,
                errors=[],
            )
            for table_name, rows in rows_by_table.items()
        }
    )


def entra_user(**overrides: Any) -> dict[str, Any]:
    user = {
        "entra_user_id": "usr-edge",
        "worker_key": "wrk-edge",
        "user_principal_name": "edge.user@example.invalid",
        "display_name": "Edge User",
        "account_enabled": True,
        "last_sign_in_date": date(2026, 8, 1),
        "account_owner_worker_key": "wrk-owner",
        "account_justification": "Documented account justification",
    }
    user.update(overrides)
    return user


def terminated_worker() -> dict[str, Any]:
    return {
        "worker_key": "wrk-edge",
        "worker_display_name": "Edge Worker",
        "worker_type": "employee",
        "worker_status": "terminated",
        "termination_date": date(2026, 7, 1),
        "contract_end_date": None,
    }


def privileged_assignment(**overrides: Any) -> dict[str, Any]:
    assignment = {
        "role_assignment_id": "pra-edge",
        "entra_user_id": "usr-edge",
        "role_name": "Global Administrator",
        "privilege_source": "direct-active",
        "owner_worker_key": "wrk-owner",
        "business_justification": "Documented assignment justification",
        "is_active_assignment": True,
    }
    assignment.update(overrides)
    return assignment


def mfa_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "mfa_record_id": "mfa-edge",
        "entra_user_id": "usr-edge",
        "has_mfa_capable_method": True,
        "registered_methods": ["phone_app_notification"],
        "default_method": "phone_app_notification",
        "mfa_registration_evidence": "Supplied data shows an MFA-capable method",
    }
    record.update(overrides)
    return record


def test_r2_unknown_active_assignment_status_triggers() -> None:
    dataset = make_dataset(
        hr_workers=[terminated_worker()],
        entra_users=[entra_user()],
        privileged_role_assignments=[privileged_assignment(is_active_assignment=None)],
    )

    findings = find_terminated_privileged_access(dataset)

    assert [(finding.evidence["entra_user_id"], finding.evidence["role_assignment_id"]) for finding in findings] == [
        ("usr-edge", "pra-edge")
    ]


def test_r2_inactive_assignment_status_does_not_trigger() -> None:
    dataset = make_dataset(
        hr_workers=[terminated_worker()],
        entra_users=[entra_user()],
        privileged_role_assignments=[privileged_assignment(is_active_assignment=False)],
    )

    assert find_terminated_privileged_access(dataset) == []


def test_r5_owner_present_but_justification_missing_triggers() -> None:
    dataset = make_dataset(
        entra_users=[entra_user(account_justification=None)],
        privileged_role_assignments=[privileged_assignment(business_justification=None)],
    )

    findings = find_privileged_missing_owner_or_justification(dataset)

    assert [(finding.evidence["entra_user_id"], finding.evidence["role_assignment_id"]) for finding in findings] == [
        ("usr-edge", "pra-edge")
    ]


def test_r5_justification_present_but_owner_missing_triggers() -> None:
    dataset = make_dataset(
        entra_users=[entra_user(account_owner_worker_key=None)],
        privileged_role_assignments=[privileged_assignment(owner_worker_key=None)],
    )

    findings = find_privileged_missing_owner_or_justification(dataset)

    assert [(finding.evidence["entra_user_id"], finding.evidence["role_assignment_id"]) for finding in findings] == [
        ("usr-edge", "pra-edge")
    ]


def test_r4_disabled_account_with_old_last_sign_in_does_not_trigger() -> None:
    dataset = make_dataset(
        entra_users=[
            entra_user(
                account_enabled=False,
                last_sign_in_date=date(2026, 1, 1),
            )
        ]
    )

    review = review_dormant_enabled_accounts(dataset)

    assert review.findings == []
    assert review.unknown_statuses == []


def test_r6_unknown_mfa_capable_status_is_unknown_not_normal_finding() -> None:
    dataset = make_dataset(
        entra_users=[entra_user()],
        mfa_registration=[mfa_record(has_mfa_capable_method=None)],
    )

    review = review_mfa_capable_registration(dataset)

    assert review.findings == []
    assert [(finding.evidence["entra_user_id"], finding.evidence["mfa_record_id"]) for finding in review.unknown_statuses] == [
        ("usr-edge", "mfa-edge")
    ]
