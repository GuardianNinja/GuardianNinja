// Cyber Busters Baton Prototype
// Playful simulation — not real cybersecurity

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const stabilityEl = document.getElementById('stability');

// World
const W = canvas.width, H = canvas.height;
const center = { x: W * 0.5, y: H * 0.6 };

let sprites = [];
let pulses = [];
let score = 0;
let firewall = 100; // percent
let time = 0;

// Baton state (twirl = angular velocity from pointer movement)
const baton = {
  x: center.x, y: center.y,
  angle: 0,
  angVel: 0, // computed from pointer delta
  radius: 28,
  cooldown: 0
};

// Containment node
const node = {
  x: W * 0.85, y: H * 0.5,
  r: 40,
  capacity: 20
};

// Home devices zone (avoid letting sprites linger here)
const homeZone = {
  x: W * 0.2, y: H * 0.5, r: 60
};

// Audio: simple WebAudio tone on pulse
const AudioCtx = window.AudioContext || window.webkitAudioContext;
const audio = new AudioCtx();

function pulseTone(freq = 440, ms = 180) {
  const osc = audio.createOscillator();
  const gain = audio.createGain();
  osc.type = 'sine';
  osc.frequency.value = freq;
  gain.gain.value = 0.08;
  osc.connect(gain).connect(audio.destination);
  osc.start();
  setTimeout(() => osc.stop(), ms);
}

// Utility
function rand(min, max) { return Math.random() * (max - min) + min; }
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }
function lerp(a, b, t) { return a + (b - a) * t; }

// Spawn rogue sprites
function spawnSprite() {
  const edge = Math.floor(rand(0,4));
  const pos = [
    { x: rand(0, W), y: -20 },
    { x: W + 20, y: rand(0, H) },
    { x: rand(0, W), y: H + 20 },
    { x: -20, y: rand(0, H) }
  ]
