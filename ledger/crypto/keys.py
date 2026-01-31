# ledger/crypto/keys.py
from dataclasses import dataclass
from dataclasses import replace
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from ledger.core.canon import canonical_json
from ledger.core.encoding import b64url_encode, b64url_decode
from ledger.core.types import Message, Proof


# Domain separation tag — very important to avoid signature reuse attacks
# across different contexts
SIGNING_DOMAIN = b"ledger:message:2026:v1"


@dataclass(frozen=True)
class AgentKeyPair:
    private_key: ed25519.Ed25519PrivateKey
    public_key: ed25519.Ed25519PublicKey

    @classmethod
    def generate(cls) -> "AgentKeyPair":
        private = ed25519.Ed25519PrivateKey.generate()
        return cls(private, private.public_key())

    def sign_bytes(self, data: bytes) -> bytes:
        """Low-level sign with domain prefix"""
        prefixed = SIGNING_DOMAIN + data
        return self.private_key.sign(prefixed)

    def verify_bytes(self, signature: bytes, data: bytes) -> bool:
        prefixed = SIGNING_DOMAIN + data
        try:
            self.public_key.verify(signature, prefixed)
            return True
        except Exception:
            return False

    def sign_message(self, msg: Message) -> Message:
        """Sign a Message and return new immutable copy with proof filled"""
        if msg.proof is not None:
            raise ValueError("Message already has proof")

        payload_dict = {k: v for k, v in msg.to_dict().items() if k != "proof"}
        canon_bytes = canonical_json(payload_dict)
        signature = self.sign_bytes(canon_bytes)

        proof = Proof(
            created=msg.timestamp,  # reuse message timestamp for simplicity
            verification_method=f"did:example:agent#{msg.agent_id}",
            proof_value=b64url_encode(signature),
        )

        return replace(msg, proof=proof)

    # Export / import helpers
    def public_key_bytes_raw(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

    def public_key_b64url(self) -> str:
        return b64url_encode(self.public_key_bytes_raw())

    @classmethod
    def from_public_b64url(cls, b64: str) -> "AgentKeyPair":
        raw = b64url_decode(b64)
        pub = ed25519.Ed25519PublicKey.from_public_bytes(raw)
        return cls(None, pub)  # type: ignore  # private=None = verify-only