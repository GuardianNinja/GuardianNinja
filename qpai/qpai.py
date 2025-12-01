#!/usr/bin/env python3
import re
from pathlib import Path

BLOCKLIST_PATH = Path(__file__).parent / "filters" / "blocklist.txt"
ALLOWLIST_PATH = Path(__file__).parent / "filters" / "allowlist.txt"

SAFE_RESPONSES = {
    "fallback": "I can’t help with that. Let’s choose a kinder, safer topic.",
    "greet": "Hey JD! I’m your QPAI. Ask me something kind, curious, or creative.",
    "kindness": "Try this: write a thank-you note, share a snack, or help someone learn.",
    "stars": "Stars are giant balls of hot gas. We see their light across huge distances—space is awe-some!",
    "learning": "Pick a small goal, practice a little each day, and celebrate tiny wins.",
}

def load_list(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

class QPAI:
    def __init__(self):
        self.block_patterns = [re.compile(re.escape(w), re.IGNORECASE) for w in load_list(BLOCKLIST_PATH)]
        self.allow_words = load_list(ALLOWLIST_PATH)

    def is_blocked(self, text: str) -> bool:
        for pat in self.block_patterns:
            if pat.search(text):
                return True
        return False

    def is_encouraged(self, text: str) -> bool:
        text_low = text.lower()
        return any(w.lower() in text_low for w in self.allow_words)

    def sanitize(self, text: str) -> str:
        # Minimal sanitation: strip whitespace and control chars
        return " ".join(text.split())

    def respond(self, prompt: str) -> str:
        p = self.sanitize(prompt)
        if not p:
            return SAFE_RESPONSES["greet"]

        if self.is_blocked(p):
            return SAFE_RESPONSES["fallback"]

        if self.is_encouraged(p):
            # Choose a friendly response based on keyword
            if "kind" in p.lower():
                return SAFE_RESPONSES["kindness"]
            if "star" in p.lower():
                return SAFE_RESPONSES["stars"]
            if "learn" in p.lower():
                return SAFE_RESPONSES["learning"]
            return "That’s a great topic! What tiny step could we take today?"

        # Neutral safe response for unlisted topics
        return "Sounds interesting! Let’s keep it kind and kid-safe. What would you like to learn or create?"

def cli():
    ai = QPAI()
    print(SAFE_RESPONSES["greet"])
    try:
        while True:
            user = input("> ")
            print
