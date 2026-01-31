# tests/test_crypto.py
import pytest
from datetime import datetime, timezone

from ledger.core.types import Message, Proof
from ledger.core.canon import canonical_json
from ledger.core.encoding import b64url_decode
from ledger.crypto.keys import AgentKeyPair
from ledger.crypto.hashing import message_hash


def utc_iso_now_ms():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@pytest.fixture
def unsigned_message():
    return Message(
        id="msg-test-0001",
        timestamp=utc_iso_now_ms(),
        session_id="sess-abc123",
        sequence=0,
        agent_id="agent:tester:001",
        agent_role="assistant",
        content="This is the first real signed test message.",
        prev_hash="",
        proof=None,
    )


def test_keypair_generate_and_export():
    kp = AgentKeyPair.generate()
    b64 = kp.public_key_b64url()
    assert len(b64) == 43  # Ed25519 public = 32 bytes → base64url 43 chars
    assert kp.public_key_b64url() == b64  # idempotent


def test_sign_and_verify_bytes():
    kp = AgentKeyPair.generate()
    data = b"important canonical payload"
    
    sig = kp.sign_bytes(data)
    assert len(sig) == 64  # Ed25519 signature size
    
    assert kp.verify_bytes(sig, data) is True
    assert kp.verify_bytes(sig, data + b"!") is False


def test_sign_message_fills_proof(unsigned_message):
    kp = AgentKeyPair.generate()
    
    signed_msg = kp.sign_message(unsigned_message)
    
    assert signed_msg.proof is not None
    assert signed_msg.proof.proof_value != ""
    assert len(signed_msg.proof.proof_value) == 86  # 64 bytes → base64url length


def test_verify_signed_message(unsigned_message):
    kp = AgentKeyPair.generate()
    signed = kp.sign_message(unsigned_message)
    
    payload_dict = {k: v for k, v in signed.to_dict().items() if k != "proof"}
    canon = canonical_json(payload_dict)
    sig_bytes = b64url_decode(signed.proof.proof_value)
    
    assert kp.verify_bytes(sig_bytes, canon) is True


def test_hash_function_consistent(unsigned_message):
    h1 = message_hash(unsigned_message)
    h2 = message_hash(unsigned_message)
    assert h1 == h2
    assert len(h1) == 64  # hex sha256