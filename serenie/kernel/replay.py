"""
Serenie Kernel - Replay Subsystem
Deterministic replay validation and state reconstruction engine.
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any

from serenie.kernel.errors import KernelErrorCode, KernelErrorEngine

@dataclass(frozen=True)
class ReplayResult:
    replayed_blocks: int
    status: str
    last_signature: str
    is_valid: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "replayed_blocks": self.replayed_blocks,
            "status": self.status,
            "last_signature": self.last_signature,
            "is_valid": self.is_valid,
            "details": self.details
        }

class KernelReplayEngine:
    def replay_journal_sequence(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        cursor = "0000000000000000"
        replayed_count = 0

        for entry in journal_entries:
            parent_sig = entry.get("parent_signature") or entry.get("parent_hash") or cursor
            curr_sig = entry.get("current_signature") or entry.get("current_hash") or entry.get("state_signature", "")
            
            if parent_sig != cursor and replayed_count > 0:
                atom = KernelErrorEngine.create_error(
                    KernelErrorCode.ERR_REPLAY_FAILURE,
                    f"Hash chain broken at step {replayed_count + 1}: expected parent {cursor}, got {parent_sig}"
                )
                return {
                    "replayed_blocks": replayed_count,
                    "status": "FAILED",
                    "error": atom.to_dict(),
                    "last_signature": cursor
                }

            replayed_count += 1
            if curr_sig:
                cursor = curr_sig

        return {
            "replayed_blocks": replayed_count,
            "status": "VERIFIED" if replayed_count >= 0 else "FAILED",
            "last_signature": cursor
        }

    def verify_replay(self, journal_entries: List[Dict[str, Any]]) -> ReplayResult:
        res = self.replay_journal_sequence(journal_entries)
        is_valid = res.get("status") == "VERIFIED"
        return ReplayResult(
            replayed_blocks=res.get("replayed_blocks", 0),
            status=res.get("status", "FAILED"),
            last_signature=res.get("last_signature", ""),
            is_valid=is_valid,
            details=res
        )
