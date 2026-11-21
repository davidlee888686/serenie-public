"""
Serenie Kernel - Error Taxonomy & Exception Subsystem
Strict, deterministic error definitions for all substrate operations.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class KernelErrorCode(str, Enum):
    ERR_CONTRACT_VIOLATION = "ERR-01-CONTRACT-VIOLATION"
    ERR_INSUFFICIENT_EVIDENCE = "ERR-02-INSUFFICIENT-EVIDENCE"
    ERR_INVALID_CANONICAL_STATE = "ERR-03-INVALID-CANONICAL-STATE"
    ERR_REPLAY_FAILURE = "ERR-04-REPLAY-FAILURE"
    ERR_UNSUPPORTED_CAPABILITY = "ERR-05-UNSUPPORTED-CAPABILITY"
    ERR_NON_CONFORMANT_TRANSFORMATION = "ERR-06-NON-CONFORMANT-TRANSFORMATION"
    ERR_DETERMINISM_BREACH = "ERR-07-DETERMINISM-BREACH"
    ERR_CEAP_VALIDATION_FAILED = "ERR-08-CEAP-VALIDATION-FAILED"
    ERR_IDENTITY_MISMATCH = "ERR-09-IDENTITY-MISMATCH"

@dataclass(frozen=True)
class KernelErrorAtom:
    code: KernelErrorCode
    message: str
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "context": self.context
        }

class SerenieKernelError(Exception):
    def __init__(self, atom: KernelErrorAtom):
        super().__init__(f"[{atom.code.value}] {atom.message}")
        self.atom = atom

class KernelErrorEngine:
    @staticmethod
    def create_error(code: KernelErrorCode, message: str, context: Optional[Dict[str, Any]] = None) -> KernelErrorAtom:
        return KernelErrorAtom(
            code=code,
            message=message,
            context=context or {}
        )

    @staticmethod
    def raise_error(code: KernelErrorCode, message: str, context: Optional[Dict[str, Any]] = None):
        atom = KernelErrorEngine.create_error(code, message, context)
        raise SerenieKernelError(atom)
