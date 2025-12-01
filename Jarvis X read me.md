# Jarvis X Scrubber

A tiny Express service that pre-scrubs incoming messages:
- Blocks hidden uploads (data URLs)
- Strips HTML/JS injection
- Flags suspicious links and domains (with an allow-list)
- Notes ghost/mirror AI textual markers (non-executable)
- Never proxies binaries — only sanitized text responses

## Run locally
```bash
npm install
npm start
