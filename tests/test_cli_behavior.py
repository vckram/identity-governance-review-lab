from __future__ import annotations

import csv
import shutil
from pathlib import Path

from identity_governance_review_lab.cli import main

DATA_DIR = Path(__file__).resolve().parents[1] / "sample-data"


def test_cli_with_sample_data_prints_validation_summary(capsys) -> None:
    exit_code = main(["--data-dir", str(DATA_DIR)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Identity Governance Review Lab validation summary" in output
    assert f"Data directory: {DATA_DIR}" in output
    assert "- hr_workers:" in output
    assert "- entra_users:" in output
    assert "Total validation errors: 0" in output


def test_cli_all_rules_prints_all_six_rule_sections(capsys) -> None:
    exit_code = main(["--data-dir", str(DATA_DIR), "--all-rules"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "R1_TERMINATED_ENABLED_ACCOUNT findings" in output
    assert "R2_TERMINATED_PRIVILEGED_ACCESS findings" in output
    assert "R3_CONTRACTOR_ACTIVE_PAST_END_DATE findings" in output
    assert "R4_DORMANT_ENABLED_ACCOUNT findings" in output
    assert "R5_PRIVILEGED_MISSING_OWNER_OR_JUSTIFICATION findings" in output
    assert "R6_NO_MFA_CAPABLE_METHOD_REGISTERED findings" in output


def test_cli_selected_rule_prints_only_that_rule_section(capsys) -> None:
    exit_code = main(["--data-dir", str(DATA_DIR), "--r3"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "R3_CONTRACTOR_ACTIVE_PAST_END_DATE findings" in output
    assert "R1_TERMINATED_ENABLED_ACCOUNT findings" not in output
    assert "R2_TERMINATED_PRIVILEGED_ACCESS findings" not in output
    assert "R4_DORMANT_ENABLED_ACCOUNT findings" not in output
    assert "R5_PRIVILEGED_MISSING_OWNER_OR_JUSTIFICATION findings" not in output
    assert "R6_NO_MFA_CAPABLE_METHOD_REGISTERED findings" not in output


def test_cli_validation_errors_prevent_rule_output(tmp_path: Path, capsys) -> None:
    bad_data_dir = tmp_path / "bad-data"
    shutil.copytree(DATA_DIR, bad_data_dir)
    remove_csv_column(bad_data_dir / "hr_workers.csv", "worker_key")

    exit_code = main(["--data-dir", str(bad_data_dir), "--all-rules"])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "missing expected column worker_key" in output
    assert "Total validation errors:" in output
    assert "Rule findings were not evaluated because validation errors were found." in output
    assert "R1_TERMINATED_ENABLED_ACCOUNT findings" not in output
    assert "R6_NO_MFA_CAPABLE_METHOD_REGISTERED findings" not in output


def test_cli_output_uses_human_review_language_without_remediation_claims(capsys) -> None:
    exit_code = main(["--data-dir", str(DATA_DIR), "--r6"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "discrepancies requiring human review, not automatic danger" in output
    assert "requires human review" in output
    assert "automatically disable" not in output.lower()
    assert "automatic remediation" not in output.lower()
    assert "modify accounts" not in output.lower()


def test_cli_report_dir_writes_markdown_reports(tmp_path: Path, capsys) -> None:
    report_dir = tmp_path / "reports"

    exit_code = main(["--data-dir", str(DATA_DIR), "--report-dir", str(report_dir)])

    output = capsys.readouterr().out
    technical_report = report_dir / "identity-review-technical.md"
    summary_report = report_dir / "identity-review-summary.md"
    assert exit_code == 0
    assert "Markdown reports written:" in output
    assert technical_report.exists()
    assert summary_report.exists()
    technical_text = technical_report.read_text(encoding="utf-8")
    summary_text = summary_report.read_text(encoding="utf-8")
    assert "synthetic data only" in technical_text
    assert "### R4_DORMANT_ENABLED_ACCOUNT Unknown Review Statuses" in technical_text
    assert "### R6_NO_MFA_CAPABLE_METHOD_REGISTERED Unknown Review Statuses" in technical_text
    assert "No R6 unknown review statuses." in technical_text
    assert "does not replace Microsoft Entra ID Governance" in summary_text
    assert "- R6_NO_MFA_CAPABLE_METHOD_REGISTERED unknown review statuses: 0" in summary_text


def test_cli_report_dir_does_not_write_reports_when_validation_errors_exist(tmp_path: Path, capsys) -> None:
    bad_data_dir = tmp_path / "bad-data"
    report_dir = tmp_path / "reports"
    shutil.copytree(DATA_DIR, bad_data_dir)
    remove_csv_column(bad_data_dir / "hr_workers.csv", "worker_key")

    exit_code = main(["--data-dir", str(bad_data_dir), "--report-dir", str(report_dir)])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "Reports were not written because validation errors were found." in output
    assert not report_dir.exists()


def remove_csv_column(path: Path, column_name: str) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    kept_fieldnames = [field for field in fieldnames if field != column_name]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=kept_fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in kept_fieldnames})
