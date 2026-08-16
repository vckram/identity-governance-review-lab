# Identity Governance Review Lab

Identity Governance Review Lab is an offline portfolio project for comparing synthetic Microsoft Entra identity records with synthetic HR worker records. The project is intended to identify identity-governance discrepancies that require human review and to produce both technical and manager-readable reporting in a later phase.

This repository is currently in the requirements phase. Phase 1 defines scope, data expectations, rule behavior, and initial design decisions only. It does not include an analysis engine, reports, tests, CI, live integrations, or sample datasets.

## Problem Statement

Organizations often need to compare identity-platform records against HR records to find accounts, access, or registration states that may no longer match the worker's current business status. In many environments, this review work is manual, inconsistent, or difficult to explain to non-technical stakeholders.

This lab demonstrates how a System Administrator with Active Directory experience can transition toward Microsoft Entra ID, IAM, and cloud-security review work by building a transparent, deterministic, offline identity review workflow.

The tool will identify discrepancies requiring human review. It will not automatically disable accounts, modify accounts, connect to a live tenant, process production data, or replace Microsoft Entra ID Governance.

## Intended Users

- Hiring managers and technical reviewers evaluating IAM and cloud-security portfolio work.
- System Administrators learning Entra ID identity-governance review concepts.
- Security, IT, or MSP stakeholders who want to understand how identity review logic could be explained through evidence-based findings.

## Version-One Scope

Version one will compare synthetic normalized Entra identity data with synthetic normalized HR worker data. It will evaluate only the six rules listed below and produce review-oriented findings in later phases.

The portfolio version is offline-first and synthetic-data-only. After the portfolio version is complete, the workflow may be evaluated for whether it could support a paid identity review assessment or future MSP product. This repository is not designing a SaaS product in version one.

## Version-One Rules

1. Terminated worker still has an enabled account.
2. Terminated worker retains privileged access.
3. Contractor remains active beyond the contract end date.
4. Dormant enabled account requires human review.
5. Privileged account has no documented owner or justification.
6. Account is not registered for an MFA-capable method according to the supplied data.

## Expected Inputs

Inputs will be synthetic files created for lab use only. Proposed normalized input areas are documented in [docs/data-schema.md](docs/data-schema.md):

- Entra users.
- Groups.
- Group memberships.
- Privileged-role assignments.
- MFA-registration information.
- HR worker records.

The normalized schema includes a stable matching identifier shared between synthetic HR and Entra records. The project will not rely only on names or email addresses for matching.

## Expected Outputs

Later phases are expected to produce:

- Technical findings with rule identifiers, evidence, and affected normalized records.
- Manager-readable summaries that explain discrepancy counts and review priorities.
- Clear language that findings require human review and are not automatic proof of malicious activity or policy violation.

No generated reports are produced in Phase 1.

## Explicit Exclusions

Version one excludes:

- Live Microsoft Graph integration.
- Live Microsoft Entra tenant connections.
- SIEM, SOC, or Splunk functionality.
- React or other web application interface.
- Automatic remediation.
- Machine-learning risk scoring.
- Multi-tenant database.
- Payment system.
- Mobile application.
- Church-specific functionality.
- SaaS architecture.
- Real personal data, production data, or customer data.
- Claims that MFA registration proves MFA enforcement.
- Claims that the project replaces Microsoft Entra ID Governance.

## Comparable Tools and Differentiation

Native Microsoft Entra ID Governance and Access Reviews, EntraFalcon, Monkey365, and commercial IGA platforms already exist.

This project is different because it is an offline synthetic portfolio lab focused on HR/Entra discrepancy review, transparent deterministic rules, and technical plus manager-readable evidence. It does not claim originality, commercial superiority, or replacement of existing Microsoft or commercial governance tools.

## Data Honesty

All data used by this project will be synthetic. Any future sample data committed to the repository must be invented for lab purposes and must not contain real worker, tenant, customer, contractor, account, or organization data.

## Copyright

Copyright © 2026 Vikramaditya Paul. All rights reserved. No permission is granted to use, copy, modify, distribute or commercially exploit this project unless a licence is added later.
