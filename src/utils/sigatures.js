import crypto from 'crypto';
import { config } from '../config.js';

// Simple HMAC verification for upstream gateway/webhook
export function verifySignature(rawBody, signatureHeader) {
  try {
    const expected = crypto.createHmac('sha256', config.webhookSecret).update(rawBody).digest('hex');
    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signatureHeader || ''));
  } catch {
    return false;
  }
}
