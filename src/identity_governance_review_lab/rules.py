from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .loader import DatasetResult

ANALYSIS_DATE = date(2026, 8, 16)
DORMANCY_THRESHOLD_DAYS = 90


@dataclass(frozen=True)
class Finding:
    rule_id: str
    description: str
    severity: str
    review_guidance: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class DormancyReview:
    findings: list[Finding]
    unknown_statuses: list[Finding]


@dataclass(frozen=True)
class MfaRegistrationReview:
    findings: list[Finding]
    unknown_statuses: list[Finding]


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


def find_contractors_active_past_end_date(
    dataset: DatasetResult,
    analysis_date: date = ANALYSIS_DATE,
) -> list[Finding]:
    """Return R3 findings for contractors with enabled accounts past contract end."""
    hr_workers = dataset.tables["hr_workers"].rows
    entra_users = dataset.tables["entra_users"].rows
    users_by_worker_key = group_entra_users_by_worker_key(entra_users)

    findings: list[Finding] = []
    for worker in hr_workers:
        if worker["worker_type"] != "contractor":
            continue

        contract_end_date = worker["contract_end_date"]
        if contract_end_date is None or contract_end_date >= analysis_date:
            continue

        worker_key = worker["worker_key"]
        if worker_key is None:
            continue

        for user in users_by_worker_key.get(worker_key, []):
            if user["account_enabled"] is True:
                findings.append(build_r3_finding(worker, user, analysis_date))

    return findings


def review_dormant_enabled_accounts(
    dataset: DatasetResult,
    analysis_date: date = ANALYSIS_DATE,
    threshold_days: int = DORMANCY_THRESHOLD_DAYS,
) -> DormancyReview:
    """Return R4 dormant findings and unknown statuses for enabled Entra users."""
    findings: list[Finding] = []
    unknown_statuses: list[Finding] = []

    for user in dataset.tables["entra_users"].rows:
        if user["account_enabled"] is not True:
            continue

        last_sign_in_date = user["last_sign_in_date"]
        if last_sign_in_date is None:
            unknown_statuses.append(build_r4_unknown_status(user, analysis_date, threshold_days))
            continue

        days_since_last_sign_in = (analysis_date - last_sign_in_date).days
        if days_since_last_sign_in >= threshold_days:
            findings.append(
                build_r4_finding(
                    user,
                    analysis_date,
                    threshold_days,
                    days_since_last_sign_in,
                )
            )

    return DormancyReview(findings=findings, unknown_statuses=unknown_statuses)


def find_privileged_missing_owner_or_justification(dataset: DatasetResult) -> list[Finding]:
    """Return R5 findings for privileged assignments missing owner or justification documentation."""
    entra_users = dataset.tables["entra_users"].rows
    role_assignments = dataset.tables["privileged_role_assignments"].rows
    users_by_id = group_entra_users_by_id(entra_users)

    findings: list[Finding] = []
    for assignment in role_assignments:
        user = users_by_id.get(assignment["entra_user_id"])
        if user is None:
            continue

        has_owner = has_value(assignment["owner_worker_key"]) or has_value(user["account_owner_worker_key"])
        has_justification = has_value(assignment["business_justification"]) or has_value(user["account_justification"])
        if not has_owner or not has_justification:
            findings.append(build_r5_finding(user, assignment))

    return findings


def review_mfa_capable_registration(dataset: DatasetResult) -> MfaRegistrationReview:
    """Return R6 findings and unknown statuses from supplied MFA-registration data."""
    entra_users = dataset.tables["entra_users"].rows
    mfa_records = dataset.tables["mfa_registration"].rows
    users_by_id = group_entra_users_by_id(entra_users)
    findings: list[Finding] = []
    unknown_statuses: list[Finding] = []

    for mfa_record in mfa_records:
        user = users_by_id.get(mfa_record["entra_user_id"])
        if user is None:
            continue

        has_mfa_capable_method = mfa_record["has_mfa_capable_method"]
        if has_mfa_capable_method is False:
            findings.append(build_r6_finding(user, mfa_record))
        elif has_mfa_capable_method is None:
            unknown_statuses.append(build_r6_unknown_status(user, mfa_record))

    return MfaRegistrationReview(findings=findings, unknown_statuses=unknown_statuses)


def group_entra_users_by_worker_key(entra_users: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    users_by_worker_key: dict[str, list[dict[str, Any]]] = {}
    for user in entra_users:
        worker_key = user["worker_key"]
        if worker_key is None:
            continue
        users_by_worker_key.setdefault(worker_key, []).append(user)
    return users_by_worker_key


def group_entra_users_by_id(entra_users: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    users_by_id: dict[str, dict[str, Any]] = {}
    for user in entra_users:
        entra_user_id = user["entra_user_id"]
        if entra_user_id is None:
            continue
        users_by_id[entra_user_id] = user
    return users_by_id


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


def has_value(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


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


def build_r3_finding(worker: dict[str, Any], user: dict[str, Any], analysis_date: date) -> Finding:
    return Finding(
        rule_id="R3_CONTRACTOR_ACTIVE_PAST_END_DATE",
        description="Contractor has a matching enabled Entra account after the contract end date.",
        severity="Medium",
        review_guidance=(
            "This is a discrepancy requiring human review. Confirm whether the contract "
            "was extended, whether HR data is current, and whether the account still "
            "requires access before any account action is considered."
        ),
        evidence={
            "worker_key": worker["worker_key"],
            "worker_display_name": worker["worker_display_name"],
            "contract_end_date": worker["contract_end_date"],
            "analysis_date": analysis_date,
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "account_enabled": user["account_enabled"],
        },
    )


def build_r4_finding(
    user: dict[str, Any],
    analysis_date: date,
    threshold_days: int,
    days_since_last_sign_in: int,
) -> Finding:
    return Finding(
        rule_id="R4_DORMANT_ENABLED_ACCOUNT",
        description="Enabled Entra account has not signed in within the configured dormancy threshold.",
        severity="Low",
        review_guidance=(
            "This is a discrepancy requiring human review. Confirm the account purpose, "
            "owner, expected sign-in pattern, and whether the account should remain "
            "enabled. This does not prove the account is unused."
        ),
        evidence={
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "display_name": user["display_name"],
            "last_sign_in_date": user["last_sign_in_date"],
            "analysis_date": analysis_date,
            "configured_dormancy_threshold_days": threshold_days,
            "days_since_last_sign_in": days_since_last_sign_in,
        },
    )


def build_r4_unknown_status(user: dict[str, Any], analysis_date: date, threshold_days: int) -> Finding:
    return Finding(
        rule_id="R4_DORMANT_ENABLED_ACCOUNT_UNKNOWN",
        description="Enabled Entra account is missing last sign-in data, so dormancy status is unknown.",
        severity="Review",
        review_guidance=(
            "This is an unknown review status requiring human review. Missing sign-in "
            "data is not clean and is not a normal dormant finding. Confirm whether "
            "sign-in data is unavailable, delayed, or stored elsewhere."
        ),
        evidence={
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "display_name": user["display_name"],
            "last_sign_in_date": user["last_sign_in_date"],
            "analysis_date": analysis_date,
            "configured_dormancy_threshold_days": threshold_days,
            "days_since_last_sign_in": None,
        },
    )


def build_r5_finding(user: dict[str, Any], assignment: dict[str, Any]) -> Finding:
    return Finding(
        rule_id="R5_PRIVILEGED_MISSING_OWNER_OR_JUSTIFICATION",
        description="Privileged-role assignment is missing documented owner or business justification.",
        severity="Medium",
        review_guidance=(
            "This is a governance documentation gap requiring human review. Confirm "
            "the business owner and reason for privileged access. This does not prove "
            "the privilege is inappropriate."
        ),
        evidence={
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "role_assignment_id": assignment["role_assignment_id"],
            "role_name": assignment["role_name"],
            "assignment_owner_worker_key": assignment["owner_worker_key"],
            "assignment_business_justification": assignment["business_justification"],
            "account_owner_worker_key": user["account_owner_worker_key"],
            "account_justification": user["account_justification"],
        },
    )


def build_r6_finding(user: dict[str, Any], mfa_record: dict[str, Any]) -> Finding:
    return Finding(
        rule_id="R6_NO_MFA_CAPABLE_METHOD_REGISTERED",
        description="Supplied MFA-registration data shows no MFA-capable registered method for the account.",
        severity="Medium",
        review_guidance=(
            "This finding is based only on the supplied MFA-registration data and "
            "requires human review. MFA registration does not prove enforcement, and "
            "lack of registration does not prove compromise."
        ),
        evidence={
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "mfa_record_id": mfa_record["mfa_record_id"],
            "has_mfa_capable_method": mfa_record["has_mfa_capable_method"],
            "registered_methods": mfa_record["registered_methods"],
            "default_method": mfa_record["default_method"],
            "mfa_registration_evidence": mfa_record["mfa_registration_evidence"],
        },
    )


def build_r6_unknown_status(user: dict[str, Any], mfa_record: dict[str, Any]) -> Finding:
    return Finding(
        rule_id="R6_NO_MFA_CAPABLE_METHOD_REGISTERED_UNKNOWN",
        description="Supplied MFA-registration data has unknown MFA-capable registration status.",
        severity="Review",
        review_guidance=(
            "This is an unknown review status requiring human review. Unknown MFA "
            "registration data is not clean and is not a normal R6 finding. MFA "
            "registration does not prove enforcement."
        ),
        evidence={
            "entra_user_id": user["entra_user_id"],
            "user_principal_name": user["user_principal_name"],
            "mfa_record_id": mfa_record["mfa_record_id"],
            "has_mfa_capable_method": mfa_record["has_mfa_capable_method"],
            "registered_methods": mfa_record["registered_methods"],
            "default_method": mfa_record["default_method"],
            "mfa_registration_evidence": mfa_record["mfa_registration_evidence"],
        },
    )
