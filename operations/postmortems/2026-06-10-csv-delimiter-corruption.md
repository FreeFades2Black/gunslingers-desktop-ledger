# Incident Post-Mortem: Semicolon Delimited European CSV Corrupting Ledger Balance

**Incident Date:** 2026-06-10  
**Impact Duration:** 30 minutes  
**Severity:** SEV-3  
**Root Cause:** A store manager imported an inventory CSV exported from a German accounting package using semicolons (`;`) as delimiters and commas (`,`) as decimal marks. Naive comma splitting parsed the entire line as a single string, resulting in NULL balance entries.

## Timeline
* **10:00 UTC:** Store operator imported monthly inventory adjustments.
* **10:05 UTC:** Account balance widget displayed `$0.00` total valuation.
* **10:15 UTC:** Developer inspected raw CSV file and identified semicolon delimiter.
* **10:22 UTC:** Implemented `csv.Sniffer` and locale-aware decimal parsing.
* **10:30 UTC:** Re-import verified clean; ledger balances reconciled to the penny.

## Corrective Actions
1. Integrated Python `csv.Sniffer` in `app.py` to automatically detect delimiter before parsing.
2. Added test case in `tests/test_ledger.py` verifying semicolon and tab delimited CSV imports.
