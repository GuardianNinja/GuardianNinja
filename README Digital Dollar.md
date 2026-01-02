# Digital Dollar — Dual‑Indexed Ledger Prototype

The **Digital Dollar** project is a ceremonial, dual‑indexed digital ledger designed to keep **personal** and **business** flows cleanly separated while enforcing **mirrored, multi‑channel authentication** at the edge.

This prototype is intentionally simple, transparent, and lineage‑safe. It is meant as a teaching tool, a starting point for experimentation, and a reference pattern for building respectful, auditable digital money systems.

---

## Core ideas

- **Dual indexing:**  
  Personal and business transactions are stored in separate lanes inside one coherent ledger object.

- **Mirrored authentication:**  
  A transaction is only accepted when device identity, user identity, and optional channels like **Bluetooth**, **RFID**, or **biometrics** agree.

- **Reverse‑engineering friction:**  
  The design assumes that any edge (router, switch, Bluetooth, RFID, biometric endpoint) can be a possible attack surface.  
  The system responds not by obscurity, but by **repeated, explicit, mirrored checks**.

- **Lineage‑safe logging:**  
  Each transaction is stored as a simple, readable, non‑exotic block (UUID, timestamp, amount, category, metadata).

---

## Project structure

```text
digital-dollar/
├─ digital_dollar.py      # Core implementation
├─ README.md              # This file
└─ LICENSE.md             # License and ceremonial usage notes
