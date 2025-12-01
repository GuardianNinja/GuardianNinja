import { z } from 'zod';
import { config } from '../config.js';

export const IncomingSchema = z.object({
  id: z.string().min(1),
  from: z.string().min(3),
  to: z.string().min(3),
  timestamp: z.number().int().positive(),
  // message body only text; no binary or base64 payloads allowed
  body: z.string().max(config.maxMessageBytes),
  // optional URLs already parsed by your gateway
  urls: z.array(z.string().url()).optional(),
  // optional headers from carrier/gateway
  meta: z.record(z.string()).optional()
});

export function validateIncoming(payload) {
  const parsed = IncomingSchema.safeParse(payload);
  if (!parsed.success) {
    return { ok: false, reason: 'schema_invalid', errors: parsed.error.issues };
  }
  return { ok: true, data: parsed.data };
}
