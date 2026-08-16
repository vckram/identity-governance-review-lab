# Requirements

## Project Status

Identity Governance Review Lab has completed the version-one portfolio scope: requirements, synthetic sample data, core CSV loading and validation, deterministic rule evaluation for the six version-one rules, CLI output, offline Markdown reports, and pytest coverage for current behavior.

## Functional Requirements

- The project shall compare synthetic normalized Microsoft Entra identity records with synthetic normalized HR worker records.
- The project shall use a stable matching identifier shared between synthetic HR and Entra records.
- The project shall not rely only on names or email addresses for matching.
- The project shall evaluate exactly six version-one rules:
  - Terminated worker still has an enabled account.
  - Terminated worker retains privileged access.
  - Contractor remains active beyond the contract end date.
  - Dormant enabled account requires human review.
  - Privileged account has no documented owner or justification.
  - Account is not registered for an MFA-capable method according to the supplied data.
- The project shall distinguish source fields supplied in input data from derived fields calculated by the tool.
- The project shall treat missing data as unknown where appropriate.
- The project shall produce evidence-based findings.
- The project shall support technical output and manager-readable output.
- The project shall support an offline Markdown technical report.
- The project shall support an offline Markdown manager-readable summary.
- The technical report shall include validation status, rule counts, detailed findings, unknown review statuses, evidence fields, and human-review guidance.
- The manager-readable summary shall include plain-language scope, aggregate counts, review priorities, and human-review next steps.
- Reports shall identify R4 and R6 unknown review statuses separately from normal findings.
- Reports shall state that findings are discrepancies requiring human review, not automatic proof of danger, compromise, or policy violation.
- Reports shall not claim that MFA registration proves MFA enforcement.
- Reports shall not claim to replace Microsoft Entra ID Governance.
- The project shall avoid automatic account modification or remediation.

## Non-Functional Requirements

- The project shall be offline-first.
- The project shall be deterministic and explainable.
- The project shall use transparent rules instead of machine-learning risk scoring.
- The project shall be suitable for a portfolio reviewer to inspect without access to a Microsoft tenant.
- The project shall keep version-one scope small enough to demonstrate IAM review concepts clearly.
- The project shall allow future configuration of the dormant-account threshold. The proposed default is 90 days.
- The project shall avoid unnecessary corporate documentation and focus on practical requirements.

## Security and Privacy Requirements

- The project shall use synthetic data only.
- The project shall not process real personal data, production data, customer data, or live tenant exports.
- The project shall not connect to Microsoft Graph or a live Microsoft Entra tenant in version one.
- The project shall not store credentials, tokens, secrets, or tenant connection details.
- Secret scanning should be considered before public publication, without adding tooling unless it is intentionally added in a later security-hardening step.
- The project shall clearly state that findings require human review.
- The project shall not claim every finding is definitively dangerous.
- The project shall not claim that MFA registration proves MFA enforcement.
- The project shall not claim to replace Microsoft Entra ID Governance.
- The repository shall exclude local input directories intended for private or real data.
- The repository may later allow committed synthetic sample data in a clearly named sample-data area.

## Acceptance Criteria

- `README.md` describes the problem statement, intended users, version-one scope, six rules, expected inputs and outputs, explicit exclusions, current project status, and synthetic-data-only position.
- `docs/data-schema.md` defines proposed normalized fields for Entra users, groups, group memberships, privileged-role assignments, MFA-registration information, and HR worker records.
- `docs/data-schema.md` identifies each field's name, data type, required status, purpose, synthetic example, and rule dependency.
- `docs/data-schema.md` includes a stable shared matching identifier between synthetic HR and Entra records.
- `docs/rules.md` documents each of the six rules with trigger conditions, evidence, severity, false positives, limitations, examples, and testable acceptance criteria.
- `docs/rules.md` includes a cautious related-control or governance-reference note for each rule without claiming compliance satisfaction.
- `docs/decisions.md` records the initial architectural and scope decisions.
- `.gitignore` excludes Python artifacts, editor files, generated reports, secrets, and local/private input data while allowing future committed synthetic sample data.
- `sample-data/` contains fictional CSV files that intentionally exercise all six version-one rules and clean cases.
- The CLI loads and validates local CSV files, prints validation summaries, and can print individual rule output or all rule output.
- The engine implements exactly the six documented version-one rules.
- The test suite covers sample-data behavior, rule edge cases, loader validation, CLI behavior, and report generation.
- Technical and manager-readable Markdown reports are generated offline from validated synthetic data.
- Reports include validation summary, finding counts, detailed evidence, unknown review statuses, limitations, and human-review language.
- Validation errors prevent rule/report output that could be mistaken for complete review results.
- Reports avoid remediation instructions, MFA enforcement claims, live tenant claims, and Microsoft Entra ID Governance replacement claims.

## Known Assumptions

- Input data will be normalized before rule evaluation.
- Microsoft-specific source exports may use different field names, but version one will document project-normalized fields rather than claiming exact Microsoft export schemas.
- `worker_key` will be the stable synthetic matching identifier shared by HR and Entra records.
- Name and email fields may help humans review records but are not sufficient as the primary match key.
- Privileged access is represented through normalized privileged-role assignment records, not inferred from every possible Entra role or group scenario.
- MFA-capable registration indicates only that the supplied data shows a capable method. It does not prove MFA is enforced at sign-in.
- The proposed dormant-account threshold is 90 days and should become configurable later.

## Known Limitations

- Version one does not connect to a live Microsoft tenant.
- Version one does not validate real Microsoft Graph API schemas.
- Version one does not remediate findings.
- Version one does not determine whether an account is malicious, compromised, or actively exploited.
- Version one does not include a web application interface.
- Version one does not provide SIEM, SOC, or Splunk functionality.
- Version one does not evaluate all identity governance controls.
- R6 reports explicit null `has_mfa_capable_method` values as unknown review statuses, but it does not currently flag Entra accounts with no matching MFA-registration record at all.
- Version one does not replace Microsoft Entra ID Governance or a formal security audit.
