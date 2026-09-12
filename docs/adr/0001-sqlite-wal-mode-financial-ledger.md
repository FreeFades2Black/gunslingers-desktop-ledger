# ADR-0001: SQLite Write-Ahead Logging (WAL) Mode for Concurrent Financial Reads

**Status:** Accepted  
**Date:** 2026-05-15  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Our desktop accounting ledger requires sub-millisecond transaction logging while background threads generate financial reports and inventory valuations without encountering `sqlite3.OperationalError: database is locked`.

## 2. Options Considered
* **Option A: Default SQLite Rollback Journal (DELETE/TRUNCATE)**
  - *Evaluation:* Full database table locks during write transactions; reader queries block writer threads, causing UI freezes in the desktop client.
* **Option B: SQLite Write-Ahead Logging (WAL Mode) with `PRAGMA synchronous = NORMAL`**
  - *Evaluation:* Readers do not block writers, and writers do not block readers; delivers 4x increase in concurrent transaction commit throughput.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (WAL Mode)**.  
**Trade-Off Accepted:** Generates secondary `-wal` and `-shm` shared memory files alongside the database file; checkpointing must be executed upon clean application shutdown.
