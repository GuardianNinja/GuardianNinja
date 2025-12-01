import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: process.env.PORT || 8080,
  webhookSecret: process.env.WEBHOOK_SECRET || 'replace-me',
  quarantineDir: process.env.QUARANTINE_DIR || './quarantine',
  allowListDomains: (process.env.ALLOW_LIST_DOMAINS || 'example.org').split(',').map(s => s.trim().toLowerCase()),
  maxMessageBytes: Number(process.env.MAX_MESSAGE_BYTES || 4096),
  enableUrlStripping: process.env.ENABLE_URL_STRIPPING === 'true',
  enableEmojiWhitelist: process.env.ENABLE_EMOJI_WHITELIST === 'true'
};
