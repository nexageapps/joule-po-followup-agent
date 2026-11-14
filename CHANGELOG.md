# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-11-14

### Added

- Joule Studio solution export for the PO Follow-up Agent (`po-followup-assistant-agent`).
- Read-only tools to flag, rank, and summarise open purchase orders, and to draft a supplier follow-up email for buyer review.
- Mock purchase order data for preview. This repository is not connected to a live S/4HANA system.
- 135 tests from the Joule Studio build, with 76% coverage.
- Community files: MIT licence, contributing guide, Contributor Covenant code of conduct, security policy, issue and pull request templates, and Dependabot for pip.

### Known issues

- PO 4500001009 was flagged as overdue even though its goods receipt shows received. The overdue rule should skip POs that are already received.
