# Operational Runbook: SQLite Database Lock Contention & Orphaned WAL Recovery

**Severity:** P2 / Desktop App Unresponsive  
**Target Systems:** Desktop SQLite Engine, File Storage

## Diagnostic Workflow

### 1. Check for Orphaned Lock and WAL Files
```powershell
Get-ChildItem -Path $env:APPDATA\GunslingersLedger -Filter "*.db*"
```
If `.db-wal` exceeds 50MB or `.db-shm` remains locked:

### 2. Force SQLite Checkpoint & Integrity Verification
```python
import sqlite3
conn = sqlite3.connect("ledger.db")
cursor = conn.cursor()
cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
cursor.execute("PRAGMA integrity_check;")
print("Integrity check:", cursor.fetchall())
conn.close()
```

### 3. Step-by-Step Remediation
1. Ensure no orphaned background processes hold database handles:
   ```powershell
   Get-Process -Name "python*" | Stop-Process -Force
   ```
2. Re-run verification suite:
   ```bash
   python -m pytest tests/test_ledger.py -v
   ```
