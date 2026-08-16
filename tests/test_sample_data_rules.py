from __future__ import annotations

from pathlib import Path

import pytest

from identity_governance_review_lab.loader import DatasetResult, load_dataset
from identity_governance_review_lab.rules import (
    find_contractors_active_past_end_date,
    find_privileged_missing_owner_or_justification,
    find_terminated_enabled_accounts,
    find_terminated_privileged_access,
    review_dormant_enabled_accounts,
    review_mfa_capable_registration,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "sample-data"


@pytest.fixture(scope="module")
def dataset() -> DatasetResult:
    return load_dataset(DATA_DIR)


def test_sample_data_validation_has_no_errors(dataset: DatasetResult) -> None:
    assert dataset.total_errors == 0


def test_r1_returns_terminated_enabled_account_only(dataset: DatasetResult) -> None:
    findings = find_terminated_enabled_accounts(dataset)

    assert [finding.evidence["entra_user_id"] for finding in findings] == ["usr-006"]


def test_r2_returns_terminated_privileged_assignment_only(dataset: DatasetResult) -> None:
    findings = find_terminated_privileged_access(dataset)

    assert [
        (finding.evidence["entra_user_id"], finding.evidence["role_assignment_id"])
        for finding in findings
    ] == [("usr-007", "pra-003")]


def test_r3_returns_contractor_past_end_date_only(dataset: DatasetResult) -> None:
    findings = find_contractors_active_past_end_date(dataset)

    assert [finding.evidence["entra_user_id"] for finding in findings] == ["usr-005"]


def test_r4_returns_dormant_and_unknown_statuses(dataset: DatasetResult) -> None:
    review = review_dormant_enabled_accounts(dataset)

    assert [finding.evidence["entra_user_id"] for finding in review.findings] == ["usr-008"]
    assert [finding.evidence["entra_user_id"] for finding in review.unknown_statuses] == ["usr-009"]


def test_r5_returns_privileged_documentation_gap_only(dataset: DatasetResult) -> None:
    findings = find_privileged_missing_owner_or_justification(dataset)

    assert [
        (finding.evidence["entra_user_id"], finding.evidence["role_assignment_id"])
        for finding in findings
    ] == [("usr-012", "pra-004")]


def test_r6_returns_no_mfa_capable_method_only(dataset: DatasetResult) -> None:
    review = review_mfa_capable_registration(dataset)

    assert [
        (finding.evidence["entra_user_id"], finding.evidence["mfa_record_id"])
        for finding in review.findings
    ] == [("usr-013", "mfa-013")]
