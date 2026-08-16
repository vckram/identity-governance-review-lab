# Decisions

This file records initial project decisions for Identity Governance Review Lab. These decisions may be revisited after the portfolio version is complete.

## D1: Offline-First

Decision: Version one will run offline and will not require a Microsoft tenant, Microsoft Graph connection, cloud database, or external service.

Rationale: The project is a portfolio lab meant to demonstrate IAM review thinking without requiring access to production systems or tenant credentials.

## D2: Synthetic Data Only

Decision: Version one will use synthetic data only.

Rationale: The project should be safe to share publicly and should not process real personal, customer, tenant, worker, contractor, or production identity data.

## D3: Human Review Instead of Remediation

Decision: Findings will identify discrepancies requiring human review. The project will not automatically disable, modify, or remediate accounts.

Rationale: Identity actions require authorization, business context, and operational change control. The lab should demonstrate review quality without implying automatic account changes.

## D4: Transparent Deterministic Rules

Decision: Version one will use transparent deterministic rules, not machine-learning risk scoring.

Rationale: Portfolio reviewers and managers should be able to understand exactly why a finding was created, what evidence supports it, and what limitations apply.

## D5: Technical and Manager-Facing Outputs

Decision: Version one supports both technical findings and manager-readable summaries.

Rationale: Identity governance work often needs to serve administrators who need evidence and leaders who need clear prioritization and plain-language explanation.

## D6: No Live Tenant Connection in Version One

Decision: Version one will not connect to a live Microsoft Entra tenant or Microsoft Graph.

Rationale: Avoiding live tenant access keeps the project safe, reproducible, and appropriate for public portfolio review.

## D7: Markdown-First Offline Reports

Decision: Initial reporting will use offline Markdown files rather than PDF, HTML, dashboards, or web UI.

Rationale: Markdown keeps the portfolio output easy to review, diff, regenerate, and inspect without additional services or publishing infrastructure.

## D8: Separate Technical and Manager-Readable Views

Decision: Reporting will provide a technical report and a separate manager-readable summary generated from the same validated synthetic data and deterministic rule findings.

Rationale: Technical reviewers need detailed evidence fields and rule identifiers, while managers need concise counts, review priorities, limitations, and plain-language next steps. Both views must preserve the same scope boundaries: synthetic data only, offline only, human review instead of remediation, no MFA enforcement claims, and no claim to replace Microsoft Entra ID Governance.

## D9: Generated Reports Are Local Artifacts

Decision: Generated reports are written to a local ignored `reports/` directory and are not committed by default.

Rationale: Reports are reproducible from the committed synthetic sample data and deterministic rules. Keeping generated reports local avoids repository noise while still letting reviewers generate and inspect the same technical and manager-readable outputs.
