from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class KernelErrorCode(str, Enum):
    ERR_CONTRACT_VIOLATION = "ERR-01-CONTRACT-VIOLATION"
    ERR_INSUFFICIENT_EVIDENCE = "ERR-02-INSUFFICIENT-EVIDENCE"
    ERR_INVALID_CANONICAL_STATE = "ERR-03-INVALID-CANONICAL-STATE"
    ERR_REPLAY_FAILURE = "ERR-04-REPLAY-FAILURE"
    ERR_UNSUPPORTED_CAPABILITY = "ERR-05-UNSUPPORTED-CAPABILITY"
    ERR_NON_CONFORMANT_TRANSFORMATION = "ERR-06-NON-CONFORMANT-TRANSFORMATION"

@dataclass(frozen=True)
class KernelErrorAtom:
    code: KernelErrorCode
    message: str
    context: Dict[str, Any]

class KernelErrorEngine:
    def raise_error(self, code: KernelErrorCode, message: str, context: Dict[str, Any] = None) -> KernelErrorAtom:
        return KernelErrorAtom(
            code=code,
            message=message,
            context=context or {}
        )
