// Minimal secure message scrubber (Jarvis X — lineage-safe)
//
// Features:
// - Text-only intake (JSON) for messages
// - Strips HTML/JS injection
// - Blocks data URLs (hidden uploads)
// - Flags suspicious phrasing
// - Flags bad/unknown domains unless allow-listed
// - Notes ghost/mirror AI textual markers (non-executable)
// - Never proxies binaries, only returns sanitized text

const express = require('express');
const helmet = require('helmet');

const app = express();
app.use(helmet());
app.use(express.json({ limit: '100kb' }));

// Configure domain allow-list via env (comma-separated), e.g. "example.org,yourcarrier.net"
const ALLOW_LIST = (process.env.ALLOW_LIST_DOMAINS || 'example.org')
  .split(',')
  .map(s => s.trim().toLowerCase());

// Basic heuristics
const suspiciousPhrases = [
  'download this',
  'free gift card',
  'verify your account',
  'urgent action required',
  'reset password here'
];

const badDomains = [
  'bit.ly',
  'tinyurl.com',
  'grabify.link',
  'iplogger.org'
];

const ghostMarkers = [
  /model\-inject\:/i,
  /prompt\-override\:/i,
  /shadow\-agent\:/i,
  /mirror\-relay\:/i,
  /silent\-watcher/i,
  /payload\-seed\:/i
];

// Util
function safeHostname(rawUrl) {
  try { return new URL(rawUrl).hostname.toLowerCase(); }
  catch { return null; }
}

function stripDangerous(body) {
  let clean = body || '';

  // Remove <script> blocks and inline handlers
  clean = clean.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gi, '[removed]');
  clean = clean.replace(/\bon\w+\s*=\s*["'][^"']*["']/gi, '[removed]');
  clean = clean.replace(/javascript:/gi, '');

  // Block data URLs (hidden uploads)
  clean = clean.replace(/data:[^;]+;base64,[A-Za-z0-9+/=]+/gi, '[blocked-data-url]');

  // Normalize whitespace
  clean = clean.replace(/\s{2,}/g, ' ').trim();

  return clean;
}

function scan(payload) {
  const advisory = [];
  const flags = { urlFlags: [], hasCodeInject: false, hasDataUrl: false, hasSuspiciousPhrase: false, ghostHints: [] };

  const body = String(payload.body || '');

  // Suspicious phrasing
  if (suspiciousPhrases.some(p => body.toLowerCase().includes(p))) {
    flags.hasSuspiciousPhrase = true;
    advisory.push('Suspicious phrasing detected.');
  }

  // Code injection hints
  if (/<script\b|javascript:|on\w+=/i.test(body)) {
    flags.hasCodeInject = true;
  }

  // Hidden upload attempts
  if (/data:[^;]+;base64,/i.test(body)) {
    flags.hasDataUrl = true;
  }

  // URLs
  const urls = Array.isArray(payload.urls) ? payload.urls : [];
  for (const u of urls) {
    const host = safeHostname(u);
    if (!host) { flags.urlFlags.push({ url: u, reason: 'invalid' }); continue; }
    if (badDomains.includes(host)) flags.urlFlags.push({ url: u, reason: 'known-bad' });
    const allowHit = ALLOW_LIST.some(d => host.endsWith(d));
    if (!allowHit) flags.urlFlags.push({ url: u, reason: 'not-allow-listed' });
  }

  // Ghost/mirror AI textual hints (non-executable)
  for (const rx of ghostMarkers) {
    if (rx.test(body)) flags.ghostHints.push(rx.source);
  }
  if (flags.ghostHints.length > 0) advisory.push('Ghost/mirror AI markers observed.');

  return { advisory, flags };
}

// Health
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'jarvis-x-scrubber' });
});

// Scrub endpoint
app.post('/scrub', (req, res) => {
  const { id, from, to, timestamp, body, urls } = req.body || {};
  // Basic schema check
  if (!id || !from || !to || typeof timestamp !== 'number' || typeof body !== 'string') {
    return res.status(400).json({ status: 'rejected', message: 'Invalid payload.' });
  }

  const { advisory, flags } = scan({ body, urls });

  // Quarantine conditions: code inject, data URL upload, or flagged URLs
  const shouldQuarantine =
    flags.hasCodeInject ||
    flags.hasDataUrl ||
    (flags.urlFlags && flags.urlFlags.length > 0);

  if (shouldQuarantine) {
    return res.status(202).json({
      status: 'quarantined',
      message: 'Suspicious content detected.',
      details: flags
    });
  }

  const cleaned = stripDangerous(body);

  return res.status(200).json({
    status: 'clean',
    message: 'Message delivered.',
    body: cleaned,
    advisory
  });
});

// Start
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`[INFO] Jarvis X Scrubber listening on :${PORT}`);
});
