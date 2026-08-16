# Data Schema

This document defines proposed normalized project fields for synthetic data. These are not claimed to be exact Microsoft Graph, Microsoft Entra admin center, or HRIS export field names unless explicitly marked as source fields in future implementation notes.

Each table identifies whether a field is a source field supplied by an input file or a derived field calculated by the future analysis engine. Missing values should be treated as unknown where appropriate, not automatically safe or dangerous.

## Shared Identifier

`worker_key` is the stable synthetic identifier used to match HR worker records to Entra user records. It should be created for the lab dataset and must not be a real employee ID, government identifier, payroll identifier, or production HR identifier.

One `worker_key` may map to more than one Entra account, such as a standard user account and a separate administrative account. Rules should evaluate each matching Entra account independently.

Names and email addresses are useful review evidence, but they are not stable enough to be the primary matching identifier.

## Privileged Access Normalization

Version-one rules evaluate privileged access through the normalized privileged-role assignments table. If future synthetic input represents privileged access through a privileged group, that access should be normalized into a privileged-role assignment with `privilege_source` such as `group-based` before R2 or R5 is evaluated.

Group records and group membership records may provide supporting context, but group-only fields are not direct triggers for version-one rules.

## Entra Users

| Field name | Type | Required | Source or derived | Purpose | Example synthetic value | Rule requires it |
|---|---|---:|---|---|---|---|
| entra_user_id | String | Yes | Source | Stable synthetic identifier for the Entra user record. | `usr-1007` | R1, R2, R3, R4, R5, R6 |
| worker_key | String | Optional | Source | Stable match key shared with HR when the account maps to a worker. | `wrk-042` | R1, R2, R3 |
| user_principal_name | String | Yes | Source | Human-readable account sign-in name for evidence and review. | `alex.chen@example.invalid` | R1, R2, R3, R4, R6 |
| display_name | String | Optional | Source | Human-readable display name for review. | `Alex Chen` | R1, R2, R3, R4, R5, R6 |
| account_enabled | Boolean | Yes | Source | Indicates whether the account is enabled in the supplied identity data. | `true` | R1, R3, R4 |
| user_type | String enum | Optional | Source | Normalized account classification such as employee, contractor, guest, service, or admin. | `contractor` | R3, R4 |
| created_date | Date | Optional | Source | Helps reviewers understand account age. | `2025-04-12` | None |
| last_sign_in_date | Date or null | Optional | Source | Most recent sign-in date in the supplied data. Null means unavailable or no sign-in recorded. | `2026-04-30` | R4 |
| department | String | Optional | Source | Business context for review. | `Finance` | None |
| manager_worker_key | String | Optional | Source | Stable synthetic worker key for the account manager, when supplied. | `wrk-010` | R5 |
| account_owner_worker_key | String | Optional | Source | Documented synthetic owner for accounts requiring ownership review. | `wrk-010` | R5 |
| account_justification | String | Optional | Source | Business justification for privileged or special-purpose accounts. | `Break-glass account for emergency tenant administration` | R5 |
| review_notes | String | Optional | Source | Optional lab notes for manual review context. | `Synthetic account used in dormant-user scenario` | None |
| days_since_last_sign_in | Integer or null | No | Derived | Number of days between analysis date and last sign-in date. Null when last sign-in is unknown. | `108` | R4 |
| dormancy_review_status | String enum | No | Derived | Represents the R4 dormancy review outcome: dormant, clean, or unknown. | `unknown` | R4 |

## Groups

| Field name | Type | Required | Source or derived | Purpose | Example synthetic value | Rule requires it |
|---|---|---:|---|---|---|---|
| group_id | String | Yes | Source | Stable synthetic identifier for the group record. | `grp-2001` | None |
| display_name | String | Yes | Source | Human-readable group name. | `Privileged Access Reviewers` | None |
| description | String | Optional | Source | Business purpose of the group. | `Synthetic group for lab review access` | None |
| group_type | String enum | Optional | Source | Normalized group type such as security, Microsoft 365, role-assignable, or distribution. | `security` | None |
| is_privileged_group | Boolean | Optional | Source | Indicates whether the supplied data labels this group as privileged for lab purposes. | `true` | None |
| owner_worker_key | String | Optional | Source | Stable synthetic worker key for the documented group owner. | `wrk-010` | None |
| access_justification | String | Optional | Source | Documented justification for privileged group use. | `Required for tenant role assignment workflow` | None |

## Group Memberships

| Field name | Type | Required | Source or derived | Purpose | Example synthetic value | Rule requires it |
|---|---|---:|---|---|---|---|
| membership_id | String | Yes | Source | Stable synthetic identifier for the membership record. | `mem-3009` | None |
| group_id | String | Yes | Source | References the normalized group. | `grp-2001` | None |
| entra_user_id | String | Yes | Source | References the normalized Entra user. | `usr-1007` | None |
| membership_type | String enum | Optional | Source | Indicates direct, nested, eligible, or unknown membership when supplied. | `direct` | None |
| assignment_start_date | Date | Optional | Source | Date the membership began, if supplied. | `2025-11-01` | None |
| assignment_end_date | Date or null | Optional | Source | Date the membership ends, if supplied. | `null` | None |

## Privileged-Role Assignments

| Field name | Type | Required | Source or derived | Purpose | Example synthetic value | Rule requires it |
|---|---|---:|---|---|---|---|
| role_assignment_id | String | Yes | Source | Stable synthetic identifier for the privileged-role assignment. | `pra-4003` | R2, R5 |
| entra_user_id | String | Yes | Source | References the normalized Entra user holding the assignment. | `usr-1007` | R2, R5 |
| role_name | String | Yes | Source | Normalized privileged role name supplied by the lab data. | `Global Administrator` | R2, R5 |
| privilege_source | String enum | Optional | Source | Indicates whether privilege is direct, group-based, eligible, active, or unknown. | `direct-active` | R2, R5 |
| assignment_start_date | Date | Optional | Source | Date the privileged assignment began, if supplied. | `2026-01-15` | None |
| assignment_end_date | Date or null | Optional | Source | Date the privileged assignment ends, if supplied. | `null` | None |
| owner_worker_key | String | Optional | Source | Documented synthetic owner for the privileged access. | `wrk-010` | R5 |
| business_justification | String | Optional | Source | Documented reason for the privileged assignment. | `Required for identity platform administration` | R5 |
| is_active_assignment | Boolean | Optional | Source | Indicates whether the supplied data says the assignment is currently active. | `true` | R2 |

## MFA-Registration Information

| Field name | Type | Required | Source or derived | Purpose | Example synthetic value | Rule requires it |
|---|---|---:|---|---|---|---|
| mfa_record_id | String | Yes | Source | Stable synthetic identifier for the MFA registration record. | `mfa-5004` | R6 |
| entra_user_id | String | Yes | Source | References the normalized Entra user. | `usr-1007` | R6 |
| has_mfa_capable_method | Boolean or null | Yes | Source | Indicates whether supplied data shows at least one MFA-capable registered method. Null means unknown. | `false` | R6 |
| registered_methods | List of strings | Optional | Source | Normalized list of registered authentication methods in the supplied data. | `["password", "email"]` | R6 |
| default_method | String or null | Optional | Source | Default method in the supplied data, if available. | `phone_app_notification` | R6 |
| registration_last_updated | Date or null | Optional | Source | Date the registration information was last updated, if supplied. | `2026-02-20` | None |
| mfa_registration_evidence | String | Optional | Source | Human-readable evidence note from the synthetic input. | `No MFA-capable method listed in supplied registration export` | R6 |

## HR Worker Records

| Field name | Type | Required | Source or derived | Purpose | Example synthetic value | Rule requires it |
|---|---|---:|---|---|---|---|
| worker_key | String | Yes | Source | Stable synthetic identifier shared with Entra users. | `wrk-042` | R1, R2, R3 |
| worker_display_name | String | Optional | Source | Human-readable worker name for review. | `Alex Chen` | R1, R2, R3 |
| worker_type | String enum | Yes | Source | Normalized worker classification such as employee or contractor. | `contractor` | R3 |
| worker_status | String enum | Yes | Source | Normalized HR status such as active, terminated, leave, or unknown. | `terminated` | R1, R2 |
| employment_start_date | Date | Optional | Source | Worker start date. | `2024-08-12` | None |
| termination_date | Date or null | Optional | Source | Date the worker was terminated, if applicable. | `2026-03-31` | R1, R2 |
| contract_end_date | Date or null | Optional | Source | Date the contractor engagement ended or is expected to end. | `2026-05-31` | R3 |
| department | String | Optional | Source | Business unit context. | `Operations` | None |
| manager_worker_key | String | Optional | Source | Stable synthetic worker key for the worker's manager. | `wrk-010` | None |
| hr_record_last_updated | Date | Optional | Source | Date the synthetic HR record was last updated. | `2026-06-01` | None |
