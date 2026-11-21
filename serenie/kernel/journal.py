"""
Serenie Kernel - Evidence Journal Subsystem
Immutable evidence ledger with clock-drift-independent hash chain provability.
"""

import json
import hashlib
import threading
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from serenie.kernel.evidence import EvidenceFact

@dataclass
class JournalEntry:
    entry_id: str
    event_type: str
    data: Dict[str, Any]
    monotonic_step: int
    parent_hash: str
    current_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "event_type": self.event_type,
            "data": self.data,
            "monotonic_step": self.monotonic_step,
            "parent_hash": self.parent_hash,
            "current_hash": self.current_hash
        }

class EvidenceJournalLedger:
    GENESIS_SIGNATURE = "0000000000000000"

    def __init__(self):
        self._lock = threading.Lock()
        self._timeline: List[Dict[str, Any]] = []
        self._last_signature = self.GENESIS_SIGNATURE
        self._global_step = 0

    def commit_fact(self, fact: EvidenceFact, state_signature: str) -> str:
        with self._lock:
            self._global_step += 1
            block = {
                "parent_signature": self._last_signature,
                "monotonic_step": self._global_step,
                "logical_timestamp": self._global_step * 1000,
                "evidence_id": fact.evidence_id,
                "contract": fact.contract_name,
                "determinism": fact.determinism_level,
                "input_coordinate": fact.input_coordinate,
                "output_coordinate": fact.output_coordinate,
                "state_signature": state_signature
            }
            
            canonical_block = json.dumps(block, sort_keys=True, separators=(',', ':'))
            current_signature = hashlib.sha256(canonical_block.encode('utf-8')).hexdigest()
            
            block["current_signature"] = current_signature
            self._timeline.append(block)
            self._last_signature = current_signature
            return current_signature

    def verify_journal_provability(self) -> bool:
        with self._lock:
            cursor = self.GENESIS_SIGNATURE
            for node in self._timeline:
                if node.get("parent_signature") != cursor and node.get("parent_hash") != cursor:
                    return False
                
                if "current_signature" in node:
                    check_target = {k: v for k, v in node.items() if k != "current_signature"}
                    canonical_str = json.dumps(check_target, sort_keys=True, separators=(',', ':'))
                    expected_sig = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
                    if node["current_signature"] != expected_sig:
                        return False
                    cursor = node["current_signature"]
                elif "current_hash" in node:
                    check_target = {k: v for k, v in node.items() if k != "current_hash"}
                    canonical_str = json.dumps(check_target, sort_keys=True, separators=(',', ':'))
                    expected_sig = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
                    if node["current_hash"] != expected_sig:
                        return False
                    cursor = node["current_hash"]
                else:
                    return False
            return True

    def clear(self):
        with self._lock:
            self._timeline.clear()
            self._last_signature = self.GENESIS_SIGNATURE
            self._global_step = 0

class KernelJournal:
    def __init__(self):
        self.ledger = EvidenceJournalLedger()
        self._entry_list: List[JournalEntry] = []

    def append(self, event_type: str, data: Dict[str, Any]) -> JournalEntry:
        step = len(self._entry_list) + 1
        parent_hash = self.ledger._last_signature
        
        block = {
            "entry_id": f"ENT-{step:04d}",
            "event_type": event_type,
            "data": data,
            "monotonic_step": step,
            "parent_hash": parent_hash
        }
        
        canonical_str = json.dumps(block, sort_keys=True, separators=(',', ':'))
        current_hash = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        
        entry = JournalEntry(
            entry_id=f"ENT-{step:04d}",
            event_type=event_type,
            data=data,
            monotonic_step=step,
            parent_hash=parent_hash,
            current_hash=current_hash
        )
        
        self._entry_list.append(entry)
        
        fact = EvidenceFact(
            evidence_id=f"EVID-{current_hash[:16].upper()}",
            contract_name=f"Journal_Event_{event_type}",
            determinism_level="D_4",
            input_coordinate=f"STEP::{step-1}",
            output_coordinate=f"STEP::{step}",
            monotonic_step=step,
            latency_seconds=0.0
        )
        self.ledger.commit_fact(fact, current_hash)
        return entry

    def entries(self) -> List[JournalEntry]:
        return list(self._entry_list)

    def verify_journal_provability(self) -> bool:
        return self.ledger.verify_journal_provability()
