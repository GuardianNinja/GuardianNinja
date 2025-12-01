import { validateIncoming } from './validators.js';
import { scanForMalware, scanUrls, scanGhostMarkers, scanUploadVectors } from './scanners.js';
import { stripDangerous } from './sanitizer.js';
import { quarantine } from './quarantine.js';

export function scrubMessage(incoming) {
  const valid = validateIncoming(incoming);
  if (!valid.ok) {
    const qid = quarantine(incoming, 'schema_invalid', { errors: valid.errors });
    return { status: 'rejected', quarantineId: qid, message: 'Invalid payload.' };
  }
  const msg = valid.data;

  const urlFlags = scanUrls(msg.urls);
  const malware = scanForMalware(msg.body);
  const ghost = scanGhostMarkers(msg.body);
  const upload = scanUploadVectors(msg.body);

  const shouldQuarantine =
    urlFlags.length > 0 ||
    malware.hasCodeInject ||
    upload.hasDataUrl;

  if (shouldQuarantine) {
    const qid = quarantine(msg, 'security_violation', { urlFlags, malware, upload });
    return { status: 'quarantined', quarantineId: qid, message: 'Suspicious content detected.' };
  }

  const cleanedBody = stripDangerous(msg.body);
  const advisory = [];

  if (malware.hasSuspicious) advisory.push('Suspicious phrasing removed/flagged.');
  if (ghost.hasGhostHints) advisory.push('Ghost/mirror AI markers observed (non-executable).');

  return {
    status: 'clean',
    message: 'Message delivered.',
    body: cleanedBody,
    advisory,
    meta: { originalLength: msg.body.length, cleanedLength: cleanedBody.length }
  };
}
