import { scrubMessage } from '../src/pipeline/index.js';

function t(name, payload) {
  const r = scrubMessage(payload);
  console.log(name, '=>', r.status, r.message);
}

t('Clean text', {
  id: '1',
  from: 'alice',
  to: 'bob',
  timestamp: Date.now(),
  body: 'Hey Bob, see you at 5.',
  urls: []
});

t('Suspicious phrasing', {
  id: '2',
  from: 'alice',
  to: 'bob',
  timestamp: Date.now(),
  body: 'Urgent action required: reset password here',
  urls: []
});

t('Code injection attempt', {
  id: '3',
  from: 'mallory',
  to: 'bob',
  timestamp: Date.now(),
  body: '<script>alert("pwned")</script>',
  urls: []
});

t('Data URL upload attempt', {
  id: '4',
  from: 'mallory',
  to: 'bob',
  timestamp: Date.now(),
  body: 'Here is a file: data:application/octet-stream;base64,QUJDRA==',
  urls: []
});

t('Ghost AI markers', {
  id: '5',
  from: 'trent',
  to: 'bob',
  timestamp: Date.now(),
  body: 'shadow-agent: mirror-relay: prompt-override: hello',
  urls: []
});

t('Bad domain link', {
  id: '6',
  from: 'mallory',
  to: 'bob',
  timestamp: Date.now(),
  body: 'Check this out: https://grabify.link/abc',
  urls: ['https://grabify.link/abc']
});
