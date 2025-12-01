# Secure Message Scrubber

A small Node.js service that pre-scrubs incoming messages, blocks hidden upload vectors, detects malware/spyware hints, and flags “ghost/mirror AI” markers before delivery. Clean messages pass; suspicious content is quarantined. No binaries are ever proxied to the client.

## Features
- Signature verification for webhook authenticity
- Schema validation (Zod)
- URL allow-list and bad-domain detection
- HTML/JS injection stripping
- Data URL blocking (prevents hidden uploads)
- Heuristic scans for “ghost/mirror AI” markers (non-executable hints)
- Quarantine with on-disk audit trail
- Configurable limits via `.env`

## Quick start
```bash
git clone <your-repo-url>
cd secure-message-scrubber
npm install
cp .env.example .env  # set WEBHOOK_SECRET, ALLOW_LIST_DOMAINS, etc.
npm run dev
