// Minimal secure message scrubber (Jarvis X — lineage-safe, omni-suit ready)
//
// Features:
// - Text-only intake (JSON) for messages
// - Strips HTML/JS injection
// - Blocks data URLs (hidden uploads)
// - Flags suspicious phrasing
// - Flags bad/unknown domains unless allow-listed
// - Notes ghost/mirror AI textual markers (non-executable)
// - Never proxies binaries, only returns sanitized text
// - Suit-agnostic identity + profiles
// - Simple adapter for any suit OS (Iron, Spider, Bat, etc.)

const express = require('express');
const helmet = require('helmet');

const app = express();
app.use(helmet());
app.use(express.json({ limit: '100kb' }));

// ---------- Identity & Suit Profiles ----------

// Runtime identity (rename-friendly)
const IDENTITY = {
  name: process.env.AI_NAME || 'Jarvis-X',
  version: process.env.AI_VERSION || '3.0-lineage-safe',
  suitProfile: (process.env.SUIT_PROFILE || 'generic').toLowerCase()
};

// Suit behavior profiles (metadata only; scrubber core stays the same)
const SUIT_PROFILES = {
  ironman: {
    hud: 'compressed',
    brightness: 'auto',
    mode: 'combat-safe'
  },
  spiderbat: {
    hud: 'minimal',
    brightness: 'stealth',
    mode: 'agile-safe'
  },
  generic: {
    hud: 'standard',
    brightness: 'normal',
    mode: 'civilian-safe'
  }
};

function getActiveProfile() {
  return SUIT_PROFILES[IDENTITY.suitProfile] || SUIT_PROFILES.generic;
}

// ---------- Config: Domain Allow-List ----------

// Configure domain allow-list via env (comma-separated), e.g. "example.org,yourcarrier.net"
const ALLOW_LIST = (process.env.ALLOW_LIST_DOMAINS || 'example.org')
  .split(',')
  .map(s => s.trim().toLowerCase());

// ---------- Heuristics ----------

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

// ---------- Utils ----------

function safeHostname(rawUrl) {
  try {
    return new URL(rawUrl).hostname.toLowerCase();
  } catch {
    return null;
  }
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
  const flags = {
    urlFlags: [],
    hasCodeInject: false,
    hasDataUrl: false,
    hasSuspiciousPhrase: false,
    ghostHints: []
  };

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
    if (!host) {
      flags.urlFlags.push({ url: u, reason: 'invalid' });
      continue;
    }
    if (badDomains.includes(host)) {
      flags.urlFlags.push({ url: u, reason: 'known-bad' });
    }
    const allowHit = ALLOW_LIST.some(d => host.endsWith(d));
    if (!allowHit) {
      flags.urlFlags.push({ url: u, reason: 'not-allow-listed' });
    }
  }

  // Ghost/mirror AI textual hints (non-executable)
  for (const rx of ghostMarkers) {
    if (rx.test(body)) {
      flags.ghostHints.push(rx.source);
    }
  }
  if (flags.ghostHints.length > 0) {
    advisory.push('Ghost/mirror AI markers observed.');
  }

  return { advisory, flags };
}

// ---------- Core Scrubber (Sanctum Layer) ----------

function scrubMessage(payload) {
  const { advisory, flags } = scan(payload);

  // Quarantine conditions: code inject, data URL upload, or flagged URLs
  const shouldQuarantine =
    flags.hasCodeInject ||
    flags.hasDataUrl ||
    (flags.urlFlags && flags.urlFlags.length > 0);

  if (shouldQuarantine) {
    return {
      statusCode: 202,
      body: {
        status: 'quarantined',
        message: 'Suspicious content detected.',
        details: flags,
        advisory,
        identity: IDENTITY,
        profile: getActiveProfile()
      }
    };
  }

  const cleaned = stripDangerous(payload.body || '');

  return {
    statusCode: 200,
    body: {
      status: 'clean',
      message: 'Message delivered.',
      body: cleaned,
      advisory,
      identity: IDENTITY,
      profile: getActiveProfile()
    }
  };
}

// ---------- Suit Adapter (for any suit OS) ----------

// This can be imported and wired into any suit runtime.
const SuitAdapter = {
  // Primary intake hook
  onMessageIntake: (payload) => {
    return scrubMessage(payload);
  },

  // Diagnostics hook
  onDiagnostics: () => {
    return {
      ok: true,
      service: 'jarvis-x-scrubber',
      identity: IDENTITY,
      profile: getActiveProfile(),
      timestamp: Date.now()
    };
  },

  // Suit event hook (no-op placeholder; suit can extend)
  onSuitEvent: (event) => {
    // In a real suit, you might log or route this.
    // Kept intentionally minimal and non-executing.
    return {
      received: true,
      eventType: event && event.type,
      at: Date.now()
    };
  }
};

// ---------- HTTP Endpoints (Backwards Compatible) ----------

// Health
app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    service: 'jarvis-x-scrubber',
    identity: IDENTITY,
    profile: getActiveProfile()
  });
});

// Optional meta endpoint for suit dashboards
app.get('/meta', (_req, res) => {
  res.json({
    identity: IDENTITY,
    profile: getActiveProfile(),
    allowList: ALLOW_LIST,
    badDomains,
    suspiciousPhrasesCount: suspiciousPhrases.length,
    ghostMarkerCount: ghostMarkers.length
  });
});

// Scrub endpoint (legacy + current)
app.post('/scrub', (req, res) => {
  const { id, from, to, timestamp, body, urls } = req.body || {};

  // Basic schema check
  if (!id || !from || !to || typeof timestamp !== 'number' || typeof body !== 'string') {
    return res.status(400).json({ status: 'rejected', message: 'Invalid payload.' });
  }

  const result = scrubMessage({ body, urls });

  return res.status(result.statusCode).json(result.body);
});

// Start server only if run directly (not when imported as a module)
if (require.main === module) {
  const PORT = process.env.PORT || 8080;
  app.listen(PORT, () => {
    console.log(
      `[INFO] ${IDENTITY.name} Scrubber (${IDENTITY.version}) listening on :${PORT} [profile=${IDENTITY.suitProfile}]`
    );
  });
}

// Export for suit runtimes and tests
module.exports = {
  app,
  SuitAdapter,
  scrubMessage,
  IDENTITY,
  getActiveProfile
};
