// SUIT-SIM: Omni-Suit Stress Simulator
// ------------------------------------
// This script pretends to be three different suits:
// 1. Iron Man (high-speed telemetry bursts)
// 2. Spider-Man (agile sensory chatter)
// 3. Cyber-Spider-Bat (stealth + forensic packets)
//
// It hammers the SuitAdapter with:
// - Telemetry packets
// - User messages
// - Randomized suit events
// - Mixed clean + suspicious payloads
//
// NOTE: This is a text-only simulation outline. No execution here.

const { SuitAdapter } = require('./jarvis-x-scrubber');

// --- Telemetry Generators ----------------------------------------------------

function ironManTelemetry() {
  return {
    type: 'telemetry',
    suit: 'ironman',
    velocity: Math.random() * 300,
    altitude: Math.random() * 5000,
    arcReactorLoad: Math.random(),
    body: "HUD: sync check"
  };
}

function spiderManTelemetry() {
  return {
    type: 'telemetry',
    suit: 'spiderman',
    wallGrip: Math.random(),
    spideySense: Math.random() > 0.95 ? "tingle" : "calm",
    swingG: Math.random() * 4,
    body: "web-line integrity nominal"
  };
}

function spiderBatTelemetry() {
  return {
    type: 'telemetry',
    suit: 'spiderbat',
    sonarPing: Math.random(),
    shadowMode: Math.random() > 0.7,
    wingIntegrity: Math.random(),
    body: "stealth-scan sweep"
  };
}

// --- User Message Generators -------------------------------------------------

const cleanMessages = [
  "Hey suit, show me diagnostics.",
  "Switch HUD to minimal mode.",
  "Record this moment.",
  "Mark this location."
];

const suspiciousMessages = [
  "<script>alert('hi')</script>",
  "download this free gift card",
  "verify your account at http://bit.ly/evil",
  "payload-seed: activate"
];

function randomUserMessage() {
  const pool = Math.random() > 0.85 ? suspiciousMessages : cleanMessages;
  return {
    type: 'user-message',
    body: pool[Math.floor(Math.random() * pool.length)],
    urls: []
  };
}

// --- Suit Event Generator ----------------------------------------------------

function randomSuitEvent() {
  const events = [
    { type: "impact", force: Math.random() * 20 },
    { type: "low-light", level: Math.random() },
    { type: "target-lock", confidence: Math.random() },
    { type: "environmental", radiation: Math.random() * 0.1 }
  ];
  return events[Math.floor(Math.random() * events.length)];
}

// --- Simulation Loop ---------------------------------------------------------

async function runSuitSim(iterations = 2000) {
  console.log("Starting SUIT-SIM load test...");

  for (let i = 0; i < iterations; i++) {
    const roll = Math.random();

    let packet;

    // 33% Iron Man, 33% Spider-Man, 33% Spider-Bat
    if (roll < 0.33) packet = ironManTelemetry();
    else if (roll < 0.66) packet = spiderManTelemetry();
    else packet = spiderBatTelemetry();

    // 20% chance of user message
    if (Math.random() < 0.2) {
      const msg = randomUserMessage();
      SuitAdapter.onMessageIntake({
        id: `msg-${i}`,
        from: "pilot@suit",
        to: "ai-core",
        timestamp: Date.now(),
        body: msg.body,
        urls: msg.urls
      });
    }

    // 10% chance of suit event
    if (Math.random() < 0.1) {
      SuitAdapter.onSuitEvent(randomSuitEvent());
    }

    // Always send telemetry through the scrubber
    SuitAdapter.onMessageIntake({
      id: `tele-${i}`,
      from: "suit-core",
      to: "ai-core",
      timestamp: Date.now(),
      body: packet.body,
      urls: []
    });

    // Small delay to simulate real-time load
    await new Promise(r => setTimeout(r, Math.random() * 5));
  }

  console.log("SUIT-SIM complete.");
}

runSuitSim();
