# ledger/ledger/__init__.py
"""
ledger — Cryptographically attested, tamper-evident logs for AI agent conversations.

Tamper-evident black-box style audit trail with Ed25519 signatures, hash chaining,
and offline verification.
"""

__version__ = "0.1.0"  # update this with each meaningful change

# Public API — these are the only names users should rely on
__all__ = [
    "Message",
    "Proof",
    "AgentKeyPair",
    "ConversationSession",
    "LogVerifier",
    "VerificationResult",
]

# Re-export the key classes for clean imports
from .core.types import Message, Proof
from .crypto.keys import AgentKeyPair
from .chain.session import ConversationSession
from .verify.verifier import LogVerifier, VerificationResult

# Optional: nice factory helpers (very user-friendly)
def create_session(session_id: str) -> ConversationSession:
    """Quick helper to start a new signed conversation session."""
    return ConversationSession(session_id=session_id)