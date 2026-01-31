# tests/test_package_imports.py
import pytest
from ledger import (
    Message,
    Proof,
    AgentKeyPair,
    ConversationSession,
    LogVerifier,
    VerificationResult,
    create_session,
)


def test_package_imports_clean():
    assert Message is not None
    assert Proof is not None
    assert AgentKeyPair is not None
    assert ConversationSession is not None
    assert LogVerifier is not None
    assert VerificationResult is not None
    assert create_session is not None


def test_smoke_end_to_end():
    alice = AgentKeyPair.generate()
    session = create_session("pytest-smoke")
    
    session.append(
        "Hello pytest!",
        "user",
        alice,
        "agent:test",
        "2026-01-31T00:00:00Z"
    )
    
    chain = session.get_chain()
    assert len(chain) == 1
    
    trusted = {"agent:test": alice.public_key_b64url()}
    verifier = LogVerifier(trusted_keys=trusted)
    result = verifier.verify(chain)
    
    assert result.is_valid is True