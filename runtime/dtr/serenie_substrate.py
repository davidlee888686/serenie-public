import time
import json
import hashlib
import threading
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional

@dataclass(frozen=True)
class CoordinateIdentity:
    logical_id: str
    version_id: str
    content_hash: str

    def to_coordinate_string(self) -> str:
        return f"{self.logical_id}::{self.version_id}::{self.content_hash[:16].upper()}"

class IdentityEngine:
    @staticmethod
    def derive_coordinate(logical_id: str, version_id: str, payload: Dict[str, Any]) -> CoordinateIdentity:
        canonical_bytes = json.dumps(
            payload, 
            sort_keys=True, 
            ensure_ascii=False,
            separators=(',', ':')
        ).replace("\r\n", "\n").encode('utf-8')
        
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()
        return CoordinateIdentity(logical_id, version_id, content_hash)

class SubstrateCanonicalizer:
    @staticmethod
    def normalize_text(raw_data: str) -> Dict[str, Any]:
        lines = [line.strip() for line in raw_data.splitlines() if line.strip()]
        normalized_content = "\n".join(lines)
        return {
            "canonical_bytes_len": len(normalized_content),
            "raw_text": normalized_content,
            "hash_fingerprint": hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()
        }

@dataclass(frozen=True)
class InvariantContract:
    name: str
    determinism_level: str
    preconditions: Dict[str, Any]

    def verify_compliance(self, normalized_payload: Dict[str, Any]) -> bool:
        text = normalized_payload.get("raw_text", "")
        if any(marker in text for marker in ["TODO", "FIXME", "XXX"]):
            return False
        return True

@dataclass(frozen=True)
class EvidenceFact:
    evidence_id: str
    contract_name: str
    determinism_level: str
    input_coordinate: str
    output_coordinate: str
    monotonic_step: int
    latency_seconds: float

class EvidenceJournalLedger:
    def __init__(self):
        self._lock = threading.Lock()
        self._timeline: List[Dict[str, Any]] = []
        self._last_signature = "0000000000000000"
        self._global_step = 0

    def commit_fact(self, fact: EvidenceFact, state_signature: str) -> str:
        with self._lock:
            self._global_step += 1
            block = {
                "parent_signature": self._last_signature,
                "monotonic_step": self._global_step,
                "timestamp_epoch": time.time(),
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
            cursor = "0000000000000000"
            for node in self._timeline:
                if node["parent_signature"] != cursor:
                    return False
                check_target = {k: v for k, v in node.items() if k != "current_signature"}
                canonical_str = json.dumps(check_target, sort_keys=True, separators=(',', ':'))
                if node["current_signature"] != hashlib.sha256(canonical_str.encode('utf-8')).hexdigest():
                    return False
                cursor = node["current_signature"]
            return True

class DeterministicRuntimeHost:
    def __init__(self):
        self.journal = EvidenceJournalLedger()

    def execute_transition(
        self, 
        logical_id: str, 
        version_id: str, 
        contract: InvariantContract, 
        raw_source: str
    ) -> Tuple[str, str]:
        
        normalized_data = SubstrateCanonicalizer.normalize_text(raw_source)
        
        if not contract.verify_compliance(normalized_data):
            raise ValueError(f"Contract {contract.name} rejected payload: Placeholders detected.")
            
        inp_coord = IdentityEngine.derive_coordinate(logical_id, version_id, normalized_data)
        
        start_time = time.perf_counter()
        html_payload = f"<html><body>{normalized_data['raw_text']}</body></html>"
        duration = time.perf_counter() - start_time
        
        out_data = {"rendered_view": html_payload, "generation_engine": "dtr.morphic.slice"}
        out_coord = IdentityEngine.derive_coordinate(logical_id, version_id, out_data)
        
        evidence_meta = {"duration": duration, "contract": contract.name}
        ev_bytes = json.dumps(evidence_meta, sort_keys=True).encode('utf-8')
        evidence_id = f"EVID-{hashlib.sha256(ev_bytes).hexdigest()[:16].upper()}"
        
        fact = EvidenceFact(
            evidence_id=evidence_id,
            contract_name=contract.name,
            determinism_level=contract.determinism_level,
            input_coordinate=inp_coord.to_coordinate_string(),
            output_coordinate=out_coord.to_coordinate_string(),
            monotonic_step=0,
            latency_seconds=duration
        )
        
        state_sig = out_coord.content_hash
        block_signature = self.journal.commit_fact(fact, state_sig)
        
        return html_payload, block_signature
