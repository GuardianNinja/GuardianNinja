import { config } from '../config.js';

export function stripDangerous(body) {
  let clean = body;

  // Remove HTML/JS injection
  clean = clean.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gi, '[removed]');
  clean = clean.replace(/\bon\w+\s*=\s*["'][^"']*["']/gi, '[removed]');
  clean = clean.replace(/javascript:/gi, '');

  // Remove data URLs (prevent hidden uploads)
  clean = clean.replace(/data:[^;]+;base64,[A-Za-z0-9+/=]+/gi, '[blocked-data-url]');

  // Optional: strip all URLs unless allow-listed
  if (config.enableUrlStripping) {
    clean = clean.replace(/\bhttps?:\/\/\S+/gi, '[link-removed]');
  }

  // Optional emoji whitelist example (keeps text+selected emojis)
  if (config.enableEmojiWhitelist) {
    clean = clean.replace(/[^\p{L}\p{N}\p{P}\p{Z}\u2764\u2600-\u26FF]/gu, '');
  }

  // Normalize whitespace
  clean = clean.replace(/\s{2,}/g, ' ').trim();

  return clean;
}
