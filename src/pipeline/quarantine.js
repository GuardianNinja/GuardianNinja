import fs from 'fs';
import path from 'path';
import { v4 as uuid } from 'uuid';
import { config } from '../config.js';
import { log } from '../utils/logger.js';

export function ensureQuarantineDir() {
  if (!fs.existsSync(config.quarantineDir)) fs.mkdirSync(config.quarantineDir, { recursive: true });
}

export function quarantine(payload, reason, details = {}) {
  ensureQuarantineDir();
  const id = uuid();
  const entry = {
    id,
    reason,
    details,
    at: Date.now(),
    payload
  };
  const file = path.join(config.quarantineDir, `${id}.json`);
  fs.writeFileSync(file, JSON.stringify(entry, null, 2), 'utf8');
  log.warn('Quarantined message', { id, reason, details });
  return id;
}
