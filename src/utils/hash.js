import crypto from 'crypto';

export function sha256(str) {
  return crypto.createHash('sha256').update(str, 'utf8').digest('hex');
}

export function contentFingerprint(obj) {
  return sha256(JSON.stringify(obj));
}
