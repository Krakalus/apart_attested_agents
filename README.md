Ledger

**Cryptographically attested, tamper-evident logs for AI agent conversations**  
Think of it as an airplane black box + content credentials for multi-agent LLM interactions.

Every message is signed with Ed25519, chained via SHA-256 hashes, and can be verified offline — even if someone tampers with history.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Features

- Per-message Ed25519 signatures
- Deterministic JSON canonicalization (RFC 8785)
- Linear hash chaining (`prev_hash`)
- Offline verification of entire chain
- Trusted key map for signature validation
- Clean top-level imports: `from ledger import ConversationSession, LogVerifier`

### Installation


# Recommended: use poetry (clean dependencies + virtualenv)
pip install poetry
poetry install

# Classic pip (editable mode for development)
pip install -e .


### Quickstart

from ledger import ConversationSession, AgentKeyPair, LogVerifier
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds") + "Z"

# Create agents
alice = AgentKeyPair.generate()
bob   = AgentKeyPair.generate()

# Start session
session = ConversationSession(session_id="conversation-001")

# Agents sign their messages
session.append(
    "Hey Bob, let's build something secure.",
    "user",
    alice,
    "agent:alice",
    utc_now()
)
session.append(
    "I'm in! Every reply signed.",
    "assistant",
    bob,
    "agent:bob",
    utc_now()
)

chain = session.get_chain()

# Verify with trusted keys
trusted = {
    "agent:alice": alice.public_key_b64url(),
    "agent:bob":   bob.public_key_b64url()
}

verifier = LogVerifier(trusted_keys=trusted)
result = verifier.verify(chain)

print(result)          # → "Chain is valid ✓"
print(result.is_valid) # → True

### Tamper Detection Example

# ... same setup as above ...

# Tamper with message #1 (change content)
tampered = chain.copy()
tampered[1] = tampered[1].replace(content="HACKED REPLY!")

result = verifier.verify(tampered)
print(result)          # → Verification FAILED ... Signature verification failed

### Project Structure

ledger/
├── ledger/                  # actual package
│   ├── __init__.py          # public API exports
│   ├── core/                # types, canonicalization, encoding
│   ├── crypto/              # key generation & signing
│   ├── chain/               # conversation sessions & chaining
│   └── verify/              # offline verifier
├── tests/                   # all pytest files
├── examples/                # runnable demos (coming soon)
├── pyproject.toml           # build & dependency config
├── README.md
└── LICENSE                  # MIT

### Running Tests

# With poetry
poetry run pytest -v

# With coverage
poetry run pytest --cov=ledger

### Development


poetry shell          # enter virtual environment
pytest -v             # run tests

### License

MIT — free to use, modify, and distribute.

### Next steps

- JSON serialization / persistence
- Merkle tree checkpoints
- LangGraph / agent framework integration
- Publish to PyPI

Contributions welcome!


