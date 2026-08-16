# Sample Data

This directory contains synthetic sample data for Identity Governance Review Lab. It is fictional lab data only and must not be treated as real worker, tenant, customer, contractor, account, or organization data.

The sample organization name used in account domains is fictional, and all user principal names use the reserved `.invalid` top-level domain.

## Review Settings

- Analysis date: `2026-08-16`
- Proposed dormancy threshold: `90` days
- Dormancy outcomes: `dormant`, `clean`, or `unknown`

`days_since_last_sign_in` and `dormancy_review_status` are included in the sample data as expected validation values for review. The analysis engine calculates or derives dormancy values for rule logic rather than blindly trusting these sample fields as input.

## CSV Files

- `hr_workers.csv`: Synthetic HR worker records, including employees, contractors, managers, active workers, and terminated workers.
- `entra_users.csv`: Synthetic normalized Entra user records matched to HR workers with `worker_key` when applicable.
- `groups.csv`: Synthetic group records used as supporting identity context.
- `group_memberships.csv`: Synthetic group membership records used as supporting identity context.
- `privileged_role_assignments.csv`: Synthetic normalized privileged-role assignments used by R2 and R5.
- `mfa_registration.csv`: Synthetic MFA-registration records used by R6.

## Intentional Rule Triggers

- R1: `usr-006` / Ellis Hart maps to `wrk-006`, which HR marks as terminated while the Entra account remains enabled.
- R2: `usr-007` / Jordan Vale maps to `wrk-007`, which HR marks as terminated while `pra-003` remains an active `Global Administrator` assignment.
- R3: `usr-005` / Priya Nair maps to contractor `wrk-005`, whose contract ended on `2026-05-31` while the Entra account remains enabled.
- R4 dormant: `usr-008` / Samira Cole is enabled and has `last_sign_in_date = 2026-03-01`, which is older than the proposed 90-day threshold as of `2026-08-16`.
- R5: `usr-012` / Legacy Ops Admin has `pra-004`, a privileged assignment with no documented owner and no documented business justification.
- R6: `usr-013` / Lina Moreno Admin has `mfa-013` with `has_mfa_capable_method = false`.

## R4 Unknown Status

- `usr-009` / Noah Finch is enabled but has a missing `last_sign_in_date`. This represents the R4 `unknown` review status. It should not be treated as clean and should not be treated as a normal dormant finding.

## Clean Records

- `usr-001` / Maya Rivers is an active manager with recent sign-in activity and documented ownership context.
- `usr-002` / Theo Grant is an active security manager with recent sign-in activity and MFA-capable registration.
- `usr-003` / Lina Moreno is an active employee with recent sign-in activity and MFA-capable registration.
- `usr-004` / Rafael Stone is an active contractor whose contract end date is after the analysis date.
- `usr-010` / Avery Quinn is a privileged user with documented owner, justification, recent sign-in activity, and MFA-capable registration.
- `usr-011` / Breakglass Identity is a special-purpose privileged account with documented owner, justification, and MFA-capable registration.

## Notes

`pra-003` includes owner and justification values so `usr-007` is mainly an R2 scenario. `usr-012` remains the intended R5 scenario for missing privileged-access documentation.

Run the CLI with `--report-dir reports` to generate local Markdown reports that summarize these synthetic scenarios.
