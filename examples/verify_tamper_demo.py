# examples/verify_tamper_demo.py
# Run with: poetry run python examples/verify_tamper_demo.py   (from repo root!)
# Shows: create signed chain → tamper → verify fails

from ledger import ConversationSession, AgentKeyPair, LogVerifier
from dataclasses import replace  # ← this is the missing import
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds") + "Z"

print("=== Ledger Tamper Detection Demo ===\n")

# Create agents
alice = AgentKeyPair.generate()
bob   = AgentKeyPair.generate()

# Start session
session = ConversationSession(session_id="demo-tamper-001")

# Normal conversation
session.append("Hey Bob, let's build a secure log.", "user", alice, "agent:alice", utc_now())
session.append("Sure Alice — signed & chained!",   "assistant", bob, "agent:bob",   utc_now())
session.append("Verify it works?",                 "user", alice, "agent:alice", utc_now())

chain = session.get_chain()
print(f"Original chain: {len(chain)} messages")

# Verify (trusted keys)
trusted = {
    "agent:alice": alice.public_key_b64url(),
    "agent:bob":   bob.public_key_b64url()
}

verifier = LogVerifier(trusted_keys=trusted)
print("Original verification:", verifier.verify(chain))

# Tamper with message #1 (change content)
tampered = chain.copy()
tampered[1] = replace(tampered[1], content="HACKED REPLY — I never said that!")  # ← fixed: use top-level replace()

print("\nAfter tampering with message #1:")
print("Tampered content:", tampered[1].content)

result = verifier.verify(tampered)
print("Tampered verification:")
print(result)
print("Detected tampering:", not result.is_valid)