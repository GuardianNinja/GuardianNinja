import express from 'express';
import helmet from 'helmet';
import { config } from './config.js';
import { log } from './utils/logger.js';
import { verifySignature } from './utils/signatures.js';
import { scrubMessage } from './pipeline/index.js';

const app = express();

// Keep raw body for signature verification
app.use(express.raw({ type: '*/*', limit: '1mb' }));
app.use(helmet());

app.post('/webhook/messages', (req, res) => {
  const signature = req.header('x-webhook-signature');
  const rawBody = req.body?.toString?.('utf8') || '';

  if (!verifySignature(rawBody, signature)) {
    return res.status(401).json({ status: 'rejected', message: 'Invalid signature.' });
  }

  // After signature check, parse JSON safely
  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return res.status(400).json({ status: 'rejected', message: 'Invalid JSON.' });
  }

  const result = scrubMessage(payload);

  // Prevent any auto-download behavior: we never proxy binaries, only text
  const safeResponse = {
    status: result.status,
    message: result.message,
    body: result.body || undefined,
    advisory: result.advisory || [],
    quarantineId: result.quarantineId || undefined
  };

  res.status(result.status === 'clean' ? 200 : 202).json(safeResponse);
});

app.get('/health', (_req, res) => res.json({ ok: true }));

app.listen(config.port, () => {
  log.info(`Secure Message Scrubber listening on :${config.port}`);
});
