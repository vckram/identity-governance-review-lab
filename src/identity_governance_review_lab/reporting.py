from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from .loader import DatasetResult
from .rules import (
    ANALYSIS_DATE,
    DORMANCY_THRESHOLD_DAYS,
    Finding,
    find_contractors_active_past_end_date,
    find_privileged_missing_owner_or_justification,
    find_terminated_enabled_accounts,
    find_terminated_privileged_access,
    review_dormant_enabled_accounts,
    review_mfa_capable_registration,
)

TECHNICAL_REPORT_NAME = "identity-review-technical.md"
SUMMARY_REPORT_NAME = "identity-review-summary.md"
UNKNOWN_STATUS_RULE_IDS = {"R4_DORMANT_ENABLED_ACCOUNT", "R6_NO_MFA_CAPABLE_METHOD_REGISTERED"}


@dataclass(frozen=True)
class RuleReport:
    rule_id: str
    findings: list[Finding]
    unknown_statuses: list[Finding]


@dataclass(frozen=True)
class ReportBundle:
    technical_markdown: str
    summary_markdown: str


def build_rule_reports(
    dataset: DatasetResult,
    analysis_date: date = ANALYSIS_DATE,
    dormancy_threshold_days: int = DORMANCY_THRESHOLD_DAYS,
) -> list[RuleReport]:
    dormancy_review = review_dormant_enabled_accounts(dataset, analysis_date, dormancy_threshold_days)
    mfa_review = review_mfa_capable_registration(dataset)

    return [
        RuleReport("R1_TERMINATED_ENABLED_ACCOUNT", find_terminated_enabled_accounts(dataset), []),
        RuleReport("R2_TERMINATED_PRIVILEGED_ACCESS", find_terminated_privileged_access(dataset), []),
        RuleReport("R3_CONTRACTOR_ACTIVE_PAST_END_DATE", find_contractors_active_past_end_date(dataset, analysis_date), []),
        RuleReport("R4_DORMANT_ENABLED_ACCOUNT", dormancy_review.findings, dormancy_review.unknown_statuses),
        RuleReport(
            "R5_PRIVILEGED_MISSING_OWNER_OR_JUSTIFICATION",
            find_privileged_missing_owner_or_justification(dataset),
            [],
        ),
        RuleReport("R6_NO_MFA_CAPABLE_METHOD_REGISTERED", mfa_review.findings, mfa_review.unknown_statuses),
    ]


def generate_reports(
    dataset: DatasetResult,
    data_dir: Path,
    analysis_date: date = ANALYSIS_DATE,
    dormancy_threshold_days: int = DORMANCY_THRESHOLD_DAYS,
) -> ReportBundle:
    rule_reports = build_rule_reports(dataset, analysis_date, dormancy_threshold_days)
    technical_markdown = render_technical_report(
        dataset,
        rule_reports,
        data_dir,
        analysis_date,
        dormancy_threshold_days,
    )
    summary_markdown = render_summary_report(
        dataset,
        rule_reports,
        data_dir,
        analysis_date,
        dormancy_threshold_days,
    )
    return ReportBundle(technical_markdown=technical_markdown, summary_markdown=summary_markdown)


def write_reports(
    report_dir: Path,
    report_bundle: ReportBundle,
) -> list[Path]:
    report_dir.mkdir(parents=True, exist_ok=True)

    technical_path = report_dir / TECHNICAL_REPORT_NAME
    summary_path = report_dir / SUMMARY_REPORT_NAME
    technical_path.write_text(report_bundle.technical_markdown, encoding="utf-8")
    summary_path.write_text(report_bundle.summary_markdown, encoding="utf-8")
    return [technical_path, summary_path]


def render_technical_report(
    dataset: DatasetResult,
    rule_reports: list[RuleReport],
    data_dir: Path,
    analysis_date: date,
    dormancy_threshold_days: int,
) -> str:
    lines = [
        "# Identity Governance Review Lab Technical Report",
        "",
        "## Scope Notice",
        "",
        "This report uses synthetic data only. It is generated offline and does not connect to a live Microsoft Entra tenant, Microsoft Graph, or any external service.",
        "",
        "Findings are discrepancies requiring human review. They are not automatic proof of danger, compromise, policy violation, or a required account change.",
        "",
        "## Analysis Metadata",
        "",
        f"- Analysis date: {analysis_date}",
        f"- Data directory: {data_dir}",
        f"- Dormancy threshold days: {dormancy_threshold_days}",
        "",
        "## Validation Summary",
        "",
    ]
    lines.extend(render_validation_summary(dataset))
    lines.extend(
        [
            "",
            "## Finding Counts",
            "",
        ]
    )
    lines.extend(render_count_summary(rule_reports))
    lines.extend(
        [
            "",
            "## Detailed Findings",
            "",
        ]
    )

    for rule_report in rule_reports:
        lines.extend(render_finding_section(rule_report.rule_id, rule_report.findings))
        if should_render_unknown_status_section(rule_report):
            lines.extend(render_unknown_status_section(rule_report.rule_id, rule_report.unknown_statuses))

    lines.extend(render_limitations_section())
    return "\n".join(lines).rstrip() + "\n"


def render_summary_report(
    dataset: DatasetResult,
    rule_reports: list[RuleReport],
    data_dir: Path,
    analysis_date: date,
    dormancy_threshold_days: int,
) -> str:
    total_findings = sum(len(rule_report.findings) for rule_report in rule_reports)
    total_unknown = sum(len(rule_report.unknown_statuses) for rule_report in rule_reports)
    lines = [
        "# Identity Governance Review Lab Manager Summary",
        "",
        "## Overview",
        "",
        "This offline summary reviews synthetic HR and Microsoft Entra-style identity data for version-one identity governance discrepancies requiring human review.",
        "",
        "It does not connect to a live tenant, modify accounts, prove compromise, prove MFA enforcement, or replace Microsoft Entra ID Governance.",
        "",
        "## Analysis Metadata",
        "",
        f"- Analysis date: {analysis_date}",
        f"- Data directory: {data_dir}",
        f"- Dormancy threshold days: {dormancy_threshold_days}",
        f"- Total records reviewed: {dataset.total_records}",
        f"- Total validation errors: {dataset.total_errors}",
        "",
        "## Review Summary",
        "",
        f"- Total normal findings: {total_findings}",
        f"- Total unknown review statuses: {total_unknown}",
    ]
    lines.extend(render_severity_counts(rule_reports))
    lines.extend(["", "## Findings By Rule", ""])
    for rule_report in rule_reports:
        lines.append(f"- {rule_report.rule_id}: {len(rule_report.findings)} finding(s)")
        if should_render_unknown_status_section(rule_report):
            lines.append(f"- {rule_report.rule_id} unknown review statuses: {len(rule_report.unknown_statuses)}")

    lines.extend(
        [
            "",
            "## Recommended Human Review",
            "",
            "- Confirm HR status and account state before considering any account action.",
            "- Review privileged access ownership and business justification.",
            "- Validate contractor end dates and documented extensions.",
            "- Confirm dormant or unknown sign-in data with the appropriate system owner.",
            "- Review supplied MFA-registration data without treating registration as proof of enforcement.",
        ]
    )
    lines.extend(render_limitations_section())
    return "\n".join(lines).rstrip() + "\n"


def render_validation_summary(dataset: DatasetResult) -> list[str]:
    lines = []
    for table_name in dataset.table_names:
        table = dataset.tables[table_name]
        lines.append(f"- {table_name}: {table.record_count} record(s), {len(table.errors)} validation error(s)")
        for error in table.errors:
            lines.append(f"  - {error}")
    lines.append(f"- Total records: {dataset.total_records}")
    lines.append(f"- Total validation errors: {dataset.total_errors}")
    return lines


def render_count_summary(rule_reports: list[RuleReport]) -> list[str]:
    lines = []
    for rule_report in rule_reports:
        lines.append(f"- {rule_report.rule_id}: {len(rule_report.findings)} finding(s)")
        if should_render_unknown_status_section(rule_report):
            lines.append(f"- {rule_report.rule_id} unknown review statuses: {len(rule_report.unknown_statuses)}")
    lines.extend(render_severity_counts(rule_reports))
    return lines


def render_severity_counts(rule_reports: list[RuleReport]) -> list[str]:
    counts: dict[str, int] = {}
    for finding in all_findings(rule_reports):
        counts[finding.severity] = counts.get(finding.severity, 0) + 1

    if not counts:
        return ["- Severity counts: none"]

    lines = ["- Severity counts:"]
    for severity in ("Critical", "High", "Medium", "Low", "Review"):
        if severity in counts:
            lines.append(f"  - {severity}: {counts[severity]}")
    return lines


def render_finding_section(rule_id: str, findings: list[Finding]) -> list[str]:
    lines = [f"### {rule_id}", ""]
    if not findings:
        return lines + [f"No {rule_id} findings.", ""]

    for index, finding in enumerate(findings, start=1):
        lines.extend(render_finding(finding, index))
    return lines


def render_unknown_status_section(rule_id: str, unknown_statuses: list[Finding]) -> list[str]:
    lines = [
        f"### {rule_id} Unknown Review Statuses",
        "",
        "These statuses require human review and are separate from normal findings.",
        "",
    ]
    if not unknown_statuses:
        lines.extend([f"No {rule_prefix(rule_id)} unknown review statuses.", ""])
        return lines

    for index, finding in enumerate(unknown_statuses, start=1):
        lines.extend(render_finding(finding, index))
    return lines


def render_finding(finding: Finding, index: int) -> list[str]:
    lines = [
        f"{index}. {finding.description}",
        f"   - Rule ID: {finding.rule_id}",
        f"   - Severity: {finding.severity}",
        f"   - Review guidance: {finding.review_guidance}",
        "   - Evidence:",
    ]
    for key, value in finding.evidence.items():
        lines.append(f"     - {key}: {format_value(value)}")
    lines.append("")
    return lines


def render_limitations_section() -> list[str]:
    return [
        "",
        "## Limitations",
        "",
        "- Reports are generated from synthetic data only.",
        "- Reports are generated offline and do not connect to a live Microsoft tenant.",
        "- Findings require human review and do not automatically prove danger, compromise, or policy violation.",
        "- The project does not automatically disable, modify, or remediate accounts.",
        "- MFA registration data does not prove MFA enforcement.",
        "- This project does not replace Microsoft Entra ID Governance.",
    ]


def all_findings(rule_reports: Iterable[RuleReport]) -> Iterable[Finding]:
    for rule_report in rule_reports:
        yield from rule_report.findings
        yield from rule_report.unknown_statuses


def should_render_unknown_status_section(rule_report: RuleReport) -> bool:
    return rule_report.rule_id in UNKNOWN_STATUS_RULE_IDS


def rule_prefix(rule_id: str) -> str:
    return rule_id.split("_", 1)[0]


def format_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)
