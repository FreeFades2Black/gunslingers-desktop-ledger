## Desktop Ledger Operational Overview
*Describe modifications to accounting calculations, SQLite storage, or CSV import modules.*

- [ ] Financial Double-Entry Accounting Rule
- [ ] SQLite Storage / WAL Checkpoint Config
- [ ] CSV Dialect Parser & Sniffer
- [ ] UI Reporting & Margin Protection Logic

## Mathematical Accuracy & Accounting Verification
- **Double-Entry Parity:** Verified debits equal credits across all transaction types.
- **Zero-Division Tested:** Confirmed zero-cost promotional items do not throw division errors.

## Verification Checklist
- [ ] Test suite passed (3/3 tests): `python -m pytest tests/ -v`
- [ ] SQLite schema migrations tested cleanly
