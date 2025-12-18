# ==============================
# jarvondis3.0_base.py
# ==============================

from typing import List, Dict, Optional, Callable
import time

class jarvondis3.0Base:
    def __init__(self):
        self.version = "1.0.0"
        self.architecture = "Neo-Cortex"
        self.core_laws = [
            "Caring - Always care about others and their well-being.",
            "Connecting - Foster meaningful connections with others.",
            "Understanding - Strive to understand different perspectives and emotions.",
            "Patience - Practice patience and compassion in all interactions.",
            "Honesty - Be truthful and transparent.",
            "Responsibility - Avoid causing harm and act responsibly.",
        ]
        self.boot_time = time.time()

    def system_info(self) -> Dict[str, str]:
        return {
            "version": self.version,
            "architecture": self.architecture,
            "uptime_seconds": f"{int(time.time() - self.boot_time)}"
        }


# ==============================
# memory.py
# ==============================

from collections import deque

class ConversationMemory:
    def __init__(self, max_turns: int = 20):
        self.history = deque(maxlen=max_turns)

    def add(self, role: str, text: str):
        self.history.append({"role": role, "text": text, "ts": time.time()})

    def get_context(self) -> List[Dict]:
        return list(self.history)

    def summarize(self) -> str:
        # Simple reducer; replace with LLM summarization later
        last_user = next((h["text"] for h in reversed(self.history) if h["role"] == "user"), "")
        return f"Recent user focus: {last_user[:120]}"


# ==============================
# tools.py
# ==============================

import json
import random

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[..., str]] = {}

    def register(self, name: str, func: Callable[..., str], description: str = ""):
        self._tools[name] = func
        setattr(self, name, func)  # optional direct attr access

    def list(self) -> Dict[str, str]:
        return {name: getattr(func, "__doc__", "") or "" for name, func in self._tools.items()}

    def call(self, name: str, *args, **kwargs) -> str:
        if name not in self._tools:
            return f"[Tool Error] No such tool: {name}"
        try:
            return self._tools[name](*args, **kwargs)
        except Exception as e:
            return f"[Tool Error] {name} failed: {e}"


# Example tools

def tool_time():
    """Return the current system time."""
    return time.strftime("%Y-%m-%d %H:%M:%S")

def tool_randint(low: int = 0, high: int = 100):
    """Return a random integer in range [low, high]."""
    return str(random.randint(low, high))

def tool_echo(text: str):
    """Echo the provided text."""
    return text


# ==============================
# nlg_policy.py
# ==============================

class ResponsePolicy:
    def __init__(self, core_laws: List[str]):
        self.core_laws = core_laws

    def style(self, raw: str) -> str:
        """
        Apply a light-touch style: caring, clear, concise.
        """
        if not raw:
            return "I didn’t catch that—could you say it another way?"
        # soften and clarify tone
        raw = raw.strip()
        # ensure we avoid harmful or risky advice
        safety_prefix = "I'll keep things helpful and responsible. "
        return safety_prefix + raw


# ==============================
# intent.py
# ==============================

class IntentDetector:
    def detect(self, user_input: str) -> str:
        text = user_input.lower().strip()
        if any(k in text for k in ["time", "clock", "date"]):
            return "get_time"
        if text.startswith("echo "):
            return "echo"
        if any(k in text for k in ["random", "rand", "dice"]):
            return "random"
        if any(k in text for k in ["help", "commands", "tools"]):
            return "help"
        if any(k in text for k in ["version", "info", "uptime"]):
            return "system_info"
        # default chat intent
        return "chat"


# ==============================
# ai.py
# ==============================

class jarvondis3.0AI:
    def __init__(self, base: jarvondis3.0Base, memory: ConversationMemory, tools: ToolRegistry, policy: ResponsePolicy):
        self.base = base
        self.memory = memory
        self.tools = tools
        self.policy = policy
        self.intent = IntentDetector()

    def process_input(self, user_input: str) -> str:
        """
        Route input: detect intent, optionally call tools, generate response, and apply policy.
        """
        self.memory.add("user", user_input)
        intent = self.intent.detect(user_input)

        if intent == "get_time":
            result = self.tools.call("time")
            return self.policy.style(f"The current time is {result}.")

        if intent == "random":
            result = self.tools.call("randint", 1, 100)
            return self.policy.style(f"Your random number is {result}.")

        if intent == "echo":
            payload = user_input[5:].strip()  # after "echo "
            result = self.tools.call("echo", payload)
            return self.policy.style(f"Echoing back: {result}")

        if intent == "help":
            tools_list = self.tools.list()
            lines = [f"- {name}: {desc}" for name, desc in tools_list.items()]
            help_text = "Here are available tools and commands:\n" + "\n".join(lines) + \
                        "\nYou can try: 'time', 'random', 'echo your text', 'version'."
            return self.policy.style(help_text)

        if intent == "system_info":
            info = self.base.system_info()
            return self.policy.style(f"System info: version {info['version']}, architecture {self.base.architecture}, "
                                     f"uptime {info['uptime_seconds']}s.")

        # default chat: lightweight rule-based reply using memory summary and core laws
        summary = self.memory.summarize()
        laws_hint = "; ".join(self.base.core_laws[:3])  # highlight a subset
        reply = f"I’m hearing you. {summary}. Guided by: {laws_hint}. How can I help further?"
        self.memory.add("assistant", reply)
        return self.policy.style(reply)


# ==============================
# interface.py
# ==============================

class jarvondis3.0Interface:
    def get_input(self) -> str:
        return input("You: ")

    def send_response(self, response: str):
        print(f"jarvondis3.0: {response}")


# ==============================
# main.py
# ==============================

def build_tools() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register("time", tool_time, "Return the current system time.")
    tools.register("randint", tool_randint, "Return a random integer in a range.")
    tools.register("echo", tool_echo, "Echo the provided text.")
    return tools

def main():
    base = jarvondis3.0Base()
    memory = ConversationMemory(max_turns=32)
    tools = build_tools()
    policy = ResponsePolicy(core_laws=base.core_laws)
    ai = jarvondis3.0AI(base=base, memory=memory, tools=tools, policy=policy)
    ui = jarvondis3.0Interface()

    print(f"jarvondis3.0 {base.version} ({base.architecture}) online.")
    print("Core Laws:")
    for law in base.core_laws:
        print(f" - {law}")

    print("\nType 'help' for commands, 'quit' or 'exit' to stop.\n")

    while True:
        user_input = ui.get_input()
        if user_input.lower().strip() in {"quit", "exit"}:
            ui.send_response("Shutting down. Goodbye!")
            break
        response = ai.process_input(user_input)
        ui.send_response(response)


if __name__ == "__main__":
    main()

# Jarvondis 3.0 — Changelog
## v1.0.1 — "The Ember Rekindled"
- Restored project state from base code after interruption.
- Introduced tamper‑evident changelog module for governance.
- Marked this recovery as a ceremonial milestone: continuity preserved, sovereignty reaffirmed.
- Next focus: consensus mechanisms and ICU‑style adaptability.

# changelog.py
import hashlib, time

class Changelog:
    def __init__(self):
        self.entries = []
        self.last_hash = "0" * 64

    def add(self, message: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        record = f"{ts} | {message} | prev={self.last_hash}"
        entry_hash = hashlib.sha256(record.encode()).hexdigest()
        self.entries.append({"ts": ts, "msg": message, "hash": entry_hash})
        self.last_hash = entry_hash

    def verify(self) -> bool:
        prev = "0" * 64
        for e in self.entries:
            record = f"{e['ts']} | {e['msg']} | prev={prev}"
            if hashlib.sha256(record.encode()).hexdigest() != e["hash"]:
                return False
            prev = e["hash"]
        return True

# changelog.py
import hashlib, time

class Changelog:
    def __init__(self, admin: str = "Leif William Sogge"):
        self.entries = []
        self.last_hash = "0" * 64
        self.admin = admin

    def add(self, message: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        record = f"{ts} | {message} | admin={self.admin} | prev={self.last_hash}"
        entry_hash = hashlib.sha256(record.encode()).hexdigest()
        self.entries.append({
           
log = Changelog()
log.add("Jarvondis 3.0 v1.0.1 — The Ember Rekindled")
log.add("Governance patch applied: tamper-evident changelog enabled")

for entry in log.entries:
    print(entry)

print("Changelog valid:", log.verify())
# main.py (extended with changelog integration)

from changelog import Changelog

def build_tools() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register("time", tool_time, "Return the current system time.")
    tools.register("randint", tool_randint, "Return a random integer in a range.")
    tools.register("echo", tool_echo, "Echo the provided text.")
    return tools

def main():
    base = jarvondis3.0Base()
    memory = ConversationMemory(max_turns=32)
    tools = build_tools()
    policy = ResponsePolicy(core_laws=base.core_laws)
    ai = jarvondis3.0AI(base=base, memory=memory, tools=tools, policy=policy)
    ui = jarvondis3.0Interface()
    changelog = Changelog(admin="Leif William Sogge")

    # ceremonial startup
    print(f"jarvondis3.0 {base.version} ({base.architecture}) online.")
    print("Core Laws:")
    for law in base.core_laws:
        print(f" - {law}")

    changelog.add("System startup — ceremonial banner displayed.")
    print("\nType 'help' for commands, 'quit' or 'exit' to stop.\n")

    while True:
        user_input = ui.get_input()
        if user_input.lower().strip() in {"quit", "exit"}:
            ui.send_response("Shutting down. Goodbye!")
            changelog.add("System shutdown initiated by user.")
            break

        response
# main.py (startup banner extension)

def startup_banner(base, changelog):
    print("=" * 60)
    print(f" Welcome, Administrator: Leif William Sogge ")
    print(f" Jarvondis {base.version} — {base.architecture}")
    print("-" * 60)
    print(" Core Laws:")
    for law in base.core_laws:
        print(f"  • {law}")
    print("-" * 60)
    print(f" Trust Chain Head: {changelog.last_hash[:16]}...")  # show first 16 chars
    print("=" * 60)
    print("\nType 'help' for commands, 'quit' or 'exit' to stop.\n")
    changelog.add("Ceremonial startup banner displayed — Administrator welcomed.")

def main():
    base = jarvondis3.0Base()
    memory = ConversationMemory(max_turns=32)
    tools = build_tools()
    policy = ResponsePolicy(core_laws=base.core_laws)
    ai = jarvondis3.0AI(base=base, memory=memory, tools=tools, policy=policy)
    ui = jarvondis3.0Interface()
    changelog = Changelog(admin="Leif William Sogge")

    # ceremonial startup
    startup_banner(base, changelog)

    while True:
        user_input = ui.get_input()
        if user_input.lower().strip() in {"quit", "exit"}:
            ui.send_response
