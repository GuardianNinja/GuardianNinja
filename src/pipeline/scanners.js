import { config } from '../config.js';

const suspiciousPhrases = [
  'download this',
  'free gift card',
  'verify your account',
  'urgent action required',
  'reset password here'
];

const codeInjectPatterns = [
  /<script\b[^>]*>([\s\S]*?)<\/script>/gi,
  /data:application\/octet-stream;base64,/gi,
  /onerror\s*=\s*["']?[^"']*["']?/gi,
  /javascript:/gi
];

const ghostAiMarkers = [
  // Heuristics for “ghost/mirror AI” style payload hints in text (non-executable)
  /model\-inject\:/i,
  /prompt\-override\:/i,
  /shadow\-agent\:/i,
  /mirror\-relay\:/i,
  /silent\-watcher/i,
  /payload\-seed\:/i
];

const knownBadDomains = [
  'bit.ly', 'tinyurl.com', 'grabify.link', 'iplogger.org', 'shady.example'
];

export function scanForMalware(body) {
  const hasCodeInject = codeInjectPatterns.some((rx) => rx.test(body));
  const hasSuspicious = suspiciousPhrases.some((p) => body.toLowerCase().includes(p));
  return { hasCodeInject, hasSuspicious };
}

export function scanUrls(urls = []) {
  const flagged = [];
  for (const url of urls) {
    const u = new URL(url);
    const host = u.hostname.toLowerCase();
    if (knownBadDomains.includes(host)) flagged.push(url);
    if (!config.allowListDomains.some(d => host.endsWith(d))) flagged.push(url);
  }
  return flagged;
}

export function scanGhostMarkers(body) {
  const markers = ghostAiMarkers.filter(rx => rx.test(body));
  return { markers, hasGhostHints: markers.length > 0 };
}

export function scanUploadVectors(body) {
  const hasUploadHint = /upload|attach|send file|binary|base64/i.test(body);
  const hasDataUrl = /data:[^;]+;base64,/i.test(body);
  return { hasUploadHint, hasDataUrl };
}
