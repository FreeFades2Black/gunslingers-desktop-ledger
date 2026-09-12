# ADR-0002: Dynamic CSV Dialect Sniffing with Mathematical Zero-Division Gross Margin Protections

**Status:** Accepted  
**Date:** 2026-06-09  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Business operators import raw transaction data exported from various POS terminals and spreadsheets. Inbound CSVs contain varied delimiters (commas, semicolons, tabs), and promotional items with $0.00 cost basis trigger catastrophic `ZeroDivisionError` crashes in gross margin calculations.

## 2. Options Considered
* **Option A: Static Comma Delimiter Assumption and Naive Margin Formula `(Price - Cost) / Cost`**
  - *Evaluation:* Crashes on non-standard delimiters; crashes immediately when cost equals zero.
* **Option B: `csv.Sniffer` Dialect Detection with Bounded Decimal Math `(Price - Cost) / max(Cost, Decimal('0.0001'))`**
  - *Evaluation:* Automatically detects delimiters, quoting characters, and line terminators; safely bounds margin calculations to protect financial reports.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Sniffer with Margin Guards)**.  
**Trade-Off Accepted:** Sniffer requires reading a 2KB sample buffer before stream parsing; guarantees 100% crash immunity on diverse input datasets.
