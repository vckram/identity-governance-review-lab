# Rules

This document defines the six version-one rules. Each rule is deterministic, evidence-based, and designed to identify discrepancies requiring human review. A finding is not an automatic statement that an account is malicious, compromised, or definitively dangerous.

Severity is proposed for prioritization only. Missing data should be treated as unknown where appropriate.

For version one, privileged access is evaluated through normalized privileged-role assignment records. If synthetic input represents privileged access through a group, that access should first be normalized into a privileged-role assignment with `privilege_source` such as `group-based`.

## R1: Terminated Worker Still Has an Enabled Account

- Rule identifier: `R1_TERMINATED_ENABLED_ACCOUNT`
- Plain-English description: A worker marked terminated in HR still has an enabled Entra account in the supplied identity data.
- Required input fields: HR `worker_key`, HR `worker_status`; Entra users `worker_key`, `entra_user_id`, `user_principal_name`, `account_enabled`. HR `termination_date` is evidence when available.
- Exact trigger condition: HR `worker_status` equals `terminated` and matching Entra `account_enabled` equals `true`.
- Proposed severity and rationale: High. A terminated worker with an enabled account may indicate delayed deprovisioning and should be reviewed promptly.
- Evidence included in the finding: `worker_key`, `worker_display_name`, `termination_date`, `entra_user_id`, `user_principal_name`, `account_enabled`.
- Recommended human review: Confirm the HR status, termination date, account ownership, business exception, and whether the account should remain enabled.
- Possible false positives: HR record is outdated; account is intentionally retained for legal hold, mailbox access, transition work, or shared historical ownership; `worker_key` match is incorrect in synthetic data.
- Limitations: The rule does not disable the account, prove misuse, or verify conditional access state.
- Related control theme / reference to verify: NIST SP 800-53 AC-2 account management; compare against the current CIS Microsoft 365 Foundations Benchmark before publication.
- Risky example: HR shows `worker_status = terminated` for `wrk-042`, termination date `2026-03-31`, and Entra shows `alex.chen@example.invalid` enabled.
- Clean example: HR shows `worker_status = terminated` for `wrk-042`, and the matching Entra account is disabled.
- Testable acceptance criteria: Given a terminated HR worker with a matching enabled Entra account, the future engine creates one R1 finding. Given a terminated HR worker with a matching disabled Entra account, it creates no R1 finding.

## R2: Terminated Worker Retains Privileged Access

- Rule identifier: `R2_TERMINATED_PRIVILEGED_ACCESS`
- Plain-English description: A worker marked terminated in HR still has an active privileged-role assignment in the supplied identity data.
- Required input fields: HR `worker_key`, HR `worker_status`; Entra users `worker_key`, `entra_user_id`, `user_principal_name`; privileged-role assignments `entra_user_id`, `role_name`, `is_active_assignment`. HR `termination_date` is evidence when available.
- Exact trigger condition: HR `worker_status` equals `terminated`, the worker matches an Entra user, and that Entra user has at least one privileged-role assignment where `is_active_assignment` equals `true` or the assignment is present and no inactive state is supplied.
- Proposed severity and rationale: Critical. Privileged access tied to a terminated worker should receive the highest review priority because it combines lifecycle discrepancy with elevated access.
- Evidence included in the finding: `worker_key`, `worker_display_name`, `termination_date`, `entra_user_id`, `user_principal_name`, `role_assignment_id`, `role_name`, `privilege_source`, `is_active_assignment`.
- Recommended human review: Confirm worker status, role assignment status, whether the assignment is eligible or active, whether an exception exists, and whether access should be removed by an authorized administrator.
- Possible false positives: Privileged assignment export is stale; role assignment is eligible but not active; HR termination is entered early or incorrectly; synthetic match key is wrong.
- Limitations: The rule does not inspect live Privileged Identity Management state, sign-in activity, or actual authorization paths beyond supplied normalized data.
- Related control theme / reference to verify: NIST SP 800-53 AC-2 account management and AC-6 least privilege; compare against the current CIS Microsoft 365 Foundations Benchmark before publication.
- Risky example: HR shows `wrk-042` terminated and Entra role assignments show `Global Administrator` with `is_active_assignment = true`.
- Clean example: HR shows `wrk-042` terminated and no privileged-role assignment exists for the matching Entra account.
- Testable acceptance criteria: Given a terminated worker matched to an Entra user with an active privileged-role assignment, the future engine creates one R2 finding per affected assignment. Given no active or supplied privileged assignment, it creates no R2 finding.

## R3: Contractor Remains Active Beyond Contract End Date

- Rule identifier: `R3_CONTRACTOR_ACTIVE_PAST_END_DATE`
- Plain-English description: A contractor has an enabled Entra account after the supplied contract end date has passed.
- Required input fields: HR `worker_key`, HR `worker_type`, HR `contract_end_date`; Entra users `worker_key`, `entra_user_id`, `user_principal_name`, `account_enabled`; analysis date.
- Exact trigger condition: HR `worker_type` equals `contractor`, HR `contract_end_date` is before the analysis date, and matching Entra `account_enabled` equals `true`.
- Proposed severity and rationale: Medium. A contractor active after contract end may be appropriate through extension, but it commonly requires validation.
- Evidence included in the finding: `worker_key`, `worker_display_name`, `contract_end_date`, analysis date, `entra_user_id`, `user_principal_name`, `account_enabled`.
- Recommended human review: Confirm whether the contract was extended, HR data was updated, and access is still required.
- Possible false positives: Contract extension has not been reflected in HR data; contract end date represents an administrative milestone rather than access end; account belongs to a returning contractor.
- Limitations: The rule does not determine whether the contractor is still performing work or whether access is currently being used.
- Related control theme / reference to verify: NIST SP 800-53 AC-2 account management; compare against the current CIS Microsoft 365 Foundations Benchmark before publication.
- Risky example: HR shows contractor `wrk-108` with `contract_end_date = 2026-05-31`, analysis date is `2026-08-16`, and Entra account is enabled.
- Clean example: HR shows contractor `wrk-108` with `contract_end_date = 2026-12-31`, and the analysis date is `2026-08-16`.
- Testable acceptance criteria: Given an enabled contractor account with contract end date before the analysis date, the future engine creates one R3 finding. Given a future contract end date or disabled account, it creates no R3 finding.

## R4: Dormant Enabled Account Requires Human Review

- Rule identifier: `R4_DORMANT_ENABLED_ACCOUNT`
- Plain-English description: An enabled Entra account has not signed in within the configured dormancy threshold.
- Required input fields: Entra users `entra_user_id`, `user_principal_name`, `account_enabled`, `last_sign_in_date`; analysis date; dormant threshold.
- Exact trigger condition: Entra `account_enabled` equals `true`, `last_sign_in_date` is known, and days between the analysis date and `last_sign_in_date` is greater than or equal to the configured dormancy threshold. The proposed default threshold is 90 days.
- Proposed severity and rationale: Low by default. Dormancy can indicate stale access, but many legitimate accounts are quiet by design.
- Evidence included in the finding: `entra_user_id`, `user_principal_name`, `display_name`, `last_sign_in_date`, analysis date, configured dormancy threshold, `days_since_last_sign_in`.
- Recommended human review: Confirm account purpose, owner, expected sign-in pattern, and whether the account should remain enabled.
- Possible false positives: Service, emergency, test, guest, or seasonal accounts may sign in rarely; last sign-in data may be unavailable or delayed; account may authenticate through paths not represented in the supplied data.
- Limitations: Missing `last_sign_in_date` must be reported as unknown review status. It is not clean, and it is not a normal R4 dormant finding. The rule does not prove the account is unused.
- Related control theme / reference to verify: NIST SP 800-53 AC-2 account management; compare against the current CIS Microsoft 365 Foundations Benchmark before publication.
- Risky example: Entra shows enabled account `legacy.admin@example.invalid` with `last_sign_in_date = 2026-03-01`, analysis date `2026-08-16`, and threshold 90 days.
- Clean example: Entra shows enabled account `sam.rivera@example.invalid` with `last_sign_in_date = 2026-08-01`, analysis date `2026-08-16`, and threshold 90 days.
- Testable acceptance criteria: Given an enabled account with known last sign-in date at least 90 days before analysis date using the default threshold, the future engine creates one R4 dormant finding. Given a missing `last_sign_in_date`, it reports unknown review status and does not create a normal R4 dormant finding. Given a known last sign-in date inside the threshold, it creates no R4 finding.

## R5: Privileged Account Has No Documented Owner or Justification

- Rule identifier: `R5_PRIVILEGED_MISSING_OWNER_OR_JUSTIFICATION`
- Plain-English description: A privileged account or privileged assignment lacks documented ownership or business justification in the supplied data.
- Required input fields: Entra users `entra_user_id`, `user_principal_name`, `account_owner_worker_key`, `account_justification`; privileged-role assignments `entra_user_id`, `role_assignment_id`, `role_name`, `owner_worker_key`, `business_justification`.
- Exact trigger condition: A privileged-role assignment exists for an Entra user and either no owner is documented at the assignment or account level, or no justification is documented at the assignment or account level.
- Proposed severity and rationale: Medium. Privileged access without ownership or justification is a governance gap, but it may be documentation debt rather than inappropriate access.
- Evidence included in the finding: `entra_user_id`, `user_principal_name`, `role_assignment_id`, `role_name`, assignment `owner_worker_key`, assignment `business_justification`, account `account_owner_worker_key`, account `account_justification`.
- Recommended human review: Identify the business owner, confirm the reason for privileged access, and document the accepted justification or remove access through normal administrative process.
- Possible false positives: Ownership or justification exists in a system not included in the synthetic input; field values may be abbreviated or stored at the group level; privileged access may be temporary but still valid.
- Limitations: The rule does not decide whether the privilege is inappropriate. It only detects missing supplied documentation.
- Related control theme / reference to verify: NIST SP 800-53 AC-2 account management and AC-6 least privilege; compare against the current CIS Microsoft 365 Foundations Benchmark before publication.
- Risky example: `breakglass01@example.invalid` has `Global Administrator` assigned, but both owner and justification fields are blank.
- Clean example: `identity.admin@example.invalid` has `Privileged Role Administrator`, documented owner `wrk-010`, and justification `Required for identity platform administration`.
- Testable acceptance criteria: Given a privileged assignment where no owner is documented at either assignment or account level, the future engine creates one R5 finding. Given a privileged assignment where no justification is documented at either assignment or account level, it creates one R5 finding. It creates no R5 finding only when both owner and justification are documented at either assignment or account level.

## R6: Account Is Not Registered for an MFA-Capable Method

- Rule identifier: `R6_NO_MFA_CAPABLE_METHOD_REGISTERED`
- Plain-English description: The supplied MFA-registration data does not show an MFA-capable method for an Entra account.
- Required input fields: Entra users `entra_user_id`, `user_principal_name`; MFA-registration information `entra_user_id`, `has_mfa_capable_method`, `registered_methods`.
- Exact trigger condition: An Entra user has an MFA-registration record where `has_mfa_capable_method` equals `false`.
- Proposed severity and rationale: Medium. Lack of an MFA-capable registered method may block stronger authentication, but registration status alone does not prove enforcement or actual sign-in protection.
- Evidence included in the finding: `entra_user_id`, `user_principal_name`, `mfa_record_id`, `has_mfa_capable_method`, `registered_methods`, `default_method`, `mfa_registration_evidence`.
- Recommended human review: Confirm current authentication-method registration, determine whether MFA is required by policy, and guide the user or owner through approved registration steps if needed.
- Possible false positives: Registration export is stale; user authenticates with a method not represented in the supplied data; account is excluded for a documented reason; account is disabled but still present in the dataset.
- Limitations: This rule does not prove MFA is enforced or not enforced. Missing MFA-registration records are unknown unless the future implementation explicitly chooses to report them separately without adding a new rule.
- Related control theme / reference to verify: NIST SP 800-53 IA-2 identification and authentication; compare against the current CIS Microsoft 365 Foundations Benchmark before publication.
- Risky example: MFA data for `alex.chen@example.invalid` lists `["password", "email"]` and `has_mfa_capable_method = false`.
- Clean example: MFA data for `sam.rivera@example.invalid` lists `["phone_app_notification"]` and `has_mfa_capable_method = true`.
- Testable acceptance criteria: Given an MFA-registration record with `has_mfa_capable_method = false`, the future engine creates one R6 finding. Given `has_mfa_capable_method = true`, it creates no R6 finding. Given a missing or null value, it treats the state as unknown rather than automatically safe.
