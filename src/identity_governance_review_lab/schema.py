from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSpec:
    name: str
    field_type: str
    required: bool


@dataclass(frozen=True)
class TableSchema:
    file_name: str
    fields: tuple[FieldSpec, ...]


SCHEMAS: dict[str, TableSchema] = {
    "hr_workers": TableSchema(
        file_name="hr_workers.csv",
        fields=(
            FieldSpec("worker_key", "string", True),
            FieldSpec("worker_display_name", "string", False),
            FieldSpec("worker_type", "string_enum", True),
            FieldSpec("worker_status", "string_enum", True),
            FieldSpec("employment_start_date", "date", False),
            FieldSpec("termination_date", "date_or_null", False),
            FieldSpec("contract_end_date", "date_or_null", False),
            FieldSpec("department", "string", False),
            FieldSpec("manager_worker_key", "string", False),
            FieldSpec("hr_record_last_updated", "date", False),
        ),
    ),
    "entra_users": TableSchema(
        file_name="entra_users.csv",
        fields=(
            FieldSpec("entra_user_id", "string", True),
            FieldSpec("worker_key", "string", False),
            FieldSpec("user_principal_name", "string", True),
            FieldSpec("display_name", "string", False),
            FieldSpec("account_enabled", "boolean", True),
            FieldSpec("user_type", "string_enum", False),
            FieldSpec("created_date", "date", False),
            FieldSpec("last_sign_in_date", "date_or_null", False),
            FieldSpec("department", "string", False),
            FieldSpec("manager_worker_key", "string", False),
            FieldSpec("account_owner_worker_key", "string", False),
            FieldSpec("account_justification", "string", False),
            FieldSpec("review_notes", "string", False),
            FieldSpec("days_since_last_sign_in", "integer_or_null", False),
            FieldSpec("dormancy_review_status", "string_enum", False),
        ),
    ),
    "groups": TableSchema(
        file_name="groups.csv",
        fields=(
            FieldSpec("group_id", "string", True),
            FieldSpec("display_name", "string", True),
            FieldSpec("description", "string", False),
            FieldSpec("group_type", "string_enum", False),
            FieldSpec("is_privileged_group", "boolean", False),
            FieldSpec("owner_worker_key", "string", False),
            FieldSpec("access_justification", "string", False),
        ),
    ),
    "group_memberships": TableSchema(
        file_name="group_memberships.csv",
        fields=(
            FieldSpec("membership_id", "string", True),
            FieldSpec("group_id", "string", True),
            FieldSpec("entra_user_id", "string", True),
            FieldSpec("membership_type", "string_enum", False),
            FieldSpec("assignment_start_date", "date", False),
            FieldSpec("assignment_end_date", "date_or_null", False),
        ),
    ),
    "privileged_role_assignments": TableSchema(
        file_name="privileged_role_assignments.csv",
        fields=(
            FieldSpec("role_assignment_id", "string", True),
            FieldSpec("entra_user_id", "string", True),
            FieldSpec("role_name", "string", True),
            FieldSpec("privilege_source", "string_enum", False),
            FieldSpec("assignment_start_date", "date", False),
            FieldSpec("assignment_end_date", "date_or_null", False),
            FieldSpec("owner_worker_key", "string", False),
            FieldSpec("business_justification", "string", False),
            FieldSpec("is_active_assignment", "boolean", False),
        ),
    ),
    "mfa_registration": TableSchema(
        file_name="mfa_registration.csv",
        fields=(
            FieldSpec("mfa_record_id", "string", True),
            FieldSpec("entra_user_id", "string", True),
            FieldSpec("has_mfa_capable_method", "boolean_or_null", True),
            FieldSpec("registered_methods", "list_of_strings", False),
            FieldSpec("default_method", "string_or_null", False),
            FieldSpec("registration_last_updated", "date_or_null", False),
            FieldSpec("mfa_registration_evidence", "string", False),
        ),
    ),
}
