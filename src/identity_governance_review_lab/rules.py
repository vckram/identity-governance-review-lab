from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .loader import DatasetResult


@dataclass(frozen=True)
class Finding:
    rule_id: str
    description: str
    severity: str
    review_guidance: str
    evidence: dict[str, Any]


def find_terminated_enabled_accounts(dataset: DatasetResult) -> list[Finding]:
    """Return R1 findings for terminated HR workers with enabled Entra accounts."""
    hr_workers = dataset.tables["hr_workers"].rows
    entra_users = dataset.tables["entra_users"].rows
    users_by_worker_key = group_entra_users_by_worker_key(entra_users)

    findings: list[Finding] = []
    for worker in hr_workers:
        if worker["worker_status"] != "terminated":
            continue

        worker_key = worker["worker_key"]
        if worker_key is None:
            continue

        for user in users_by_worker_key.get(worker_key, []):
            if user["account_enabled"] is True:
                findings.append(build_r1_finding(worker, user))

    return findings


def find_terminated_privileged_access(dataset: DatasetResult) -> list[Finding]:
    """Return R2 findings for terminated HR workers retaining privileged access."""
    hr_workers = dataset.tables["hr_workers"].rows
    entra_users = dataset.tables["entra_users"].rows
    role_assignments = dataset.tables["privileged_role_assignments"].rows
    users_by_worker_key = group_entra_users_by_worker_key(entra_users)
    assignments_by_user_id = group_role_assignments_by_user_id(role_assignments)

    findings: list[Finding] = []
    for worker in hr_workers:
        if worker["worker_status"] != "terminated":
            continue

        worker_key = worker["worker_key"]
        if worker_key is None:
            continue

        for user in users_by_worker_key.get(worker_key, []):
            for assignment in assignments_by_user_id.get(user["entra_user_id"], []):
                if assignment["is_active_assignment"] is not False:
                    findings.append(build_r2_finding(worker, user, assignment))

    return findings


def group_entra_users_by_worker_key(entra_users: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    users_by_worker_key: dict[str, list[dict[str, Any]]] = {}
    for user in entra_users:
        worker_key = user["worker_key"]
        if worker_key is None:
            continue
        users_by_worker_key.setdefault(worker_key, []).append(user)
    return users_by_worker_key


def group_role_assignments_by_user_id(
    role_assignments: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    assignments_by_user_id: dict[str, list[dict[str, Any]]] = {}
    for assignment in role_assignments:
        entra_user_id = assignment["entra_user_id"]
        if entra_user_id is None:
            continue
        assignments_by_user_id.setdefault(entra_user_id, []).append(assignment)
    return assignments_by_user_id


def build_r1_finding(worker: dict[str, Any], user: dict[str, Any]) -> Finding:
    return Finding(
        rule_id="R1_TERMINATED_ENABLED_ACCOUNT",
        description="Terminated HR worker has a matching enabled Entra account.",
        severity="High",
        review_guidance=(
            "This is a discrepancy requiring human review. Confirm the HR status, "
            "termination date, account ownership, and whether a documented business "
            "exception exists before any account action is considered."
        ),
        evidence={
            "worker_key": worker["worker_key"],
            "worker_display_name": worker["worker_display_name"],
            "termination_date": worker["termination_date"],
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "account_enabled": user["account_enabled"],
        },
    )


def build_r2_finding(worker: dict[str, Any], user: dict[str, Any], assignment: dict[str, Any]) -> Finding:
    return Finding(
        rule_id="R2_TERMINATED_PRIVILEGED_ACCESS",
        description="Terminated HR worker has a matching active or unknown-status privileged-role assignment.",
        severity="Critical",
        review_guidance=(
            "This is a discrepancy requiring human review. Confirm the HR status, "
            "privileged assignment status, whether an exception exists, and whether "
            "access should be changed through an authorized administrative process."
        ),
        evidence={
            "worker_key": worker["worker_key"],
            "worker_display_name": worker["worker_display_name"],
            "termination_date": worker["termination_date"],
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "role_assignment_id": assignment["role_assignment_id"],
            "role_name": assignment["role_name"],
            "privilege_source": assignment["privilege_source"],
            "is_active_assignment": assignment["is_active_assignment"],
        },
    )
