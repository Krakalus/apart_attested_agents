# ledger/crypto/hashing.py
import hashlib

from ledger.core.canon import canonical_json
from ledger.core.types import Message


def message_hash(msg: Message) -> str:
    """
    SHA-256 of the canonical JSON representation.
    Used for prev_hash field.
    """
    canon = canonical_json(msg.to_dict())
    return hashlib.sha256(canon).hexdigest()