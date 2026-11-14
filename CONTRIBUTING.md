# Contributing

This repository is an SAP Joule Studio solution export. It is not a standalone application.

## Report an issue

Open a GitHub issue. Describe what you expected, what happened, and how to reproduce it. Do not include credentials, tokens, or real purchase order or supplier data. Use the included mock data only.

## Propose a change

1. Open a pull request with a short summary of the change.
2. Test the change in Joule Studio before you ask for review. Import the export, run the tests, and preview the agent.
3. Describe that testing in the pull request.

## Data and credentials

Never commit credentials, secrets, or real purchase order data. The export previews against mock PO data in `assets/po-followup-assistant-agent/app/mock_po_data.py`. Keep it that way.

## Conduct and security

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md).
