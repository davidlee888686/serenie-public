"""
Serenie Kernel - Evidence Subsystem
Cryptographic evidence facts and determinism level classification (D_0 to D_4).
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

VALID_DETERMINISM_LEVELS = {"D_0", "D_1", "D_2", "D_3", "D_4"}

@dataclass(frozen=True)
class EvidenceFact:
    evidence_id: str
    contract_name: str
    determinism_level: str
    input_coordinate: str
    output_coordinate: str
    monotonic_step: int
    latency_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "contract_name": self.contract_name,
            "determinism_level": self.determinism_level,
            "input_coordinate": self.input_coordinate,
            "output_coordinate": self.output_coordinate,
            "monotonic_step": self.monotonic_step,
            "latency_seconds": self.latency_seconds
        }

class EvidenceEngine:
    @staticmethod
    def generate_evidence_id(
        contract_name: str, 
        input_coordinate: str, 
        output_coordinate: str,
        monotonic_step: int
    ) -> str:
        payload = f"{contract_name}:{input_coordinate}:{output_coordinate}:{monotonic_step}".encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()[:16].upper()
        return f"EVID-{digest}"

    @staticmethod
    def create_fact(
        contract_name: str,
        determinism_level: str,
        input_coordinate: str,
        output_coordinate: str,
        monotonic_step: int,
        latency_seconds: float = 0.0
    ) -> EvidenceFact:
        if determinism_level not in VALID_DETERMINISM_LEVELS:
            raise ValueError(f"Invalid determinism level: '{determinism_level}'. Must be one of {VALID_DETERMINISM_LEVELS}")
            
        evidence_id = EvidenceEngine.generate_evidence_id(
            contract_name, input_coordinate, output_coordinate, monotonic_step
        )
        return EvidenceFact(
            evidence_id=evidence_id,
            contract_name=contract_name,
            determinism_level=determinism_level,
            input_coordinate=input_coordinate,
            output_coordinate=output_coordinate,
            monotonic_step=monotonic_step,
            latency_seconds=latency_seconds
        )

def create_evidence(
    logical_id: str, 
    version_id: Any, 
    content_hash: str, 
    context: Optional[Dict[str, Any]] = None
) -> EvidenceFact:
    input_coord = f"{logical_id}::{version_id}::{content_hash[:16].upper()}"
    output_coord = f"{logical_id}::{version_id}::EXEC-{content_hash[:16].upper()}"
    return EvidenceEngine.create_fact(
        contract_name="Default_Evidence_Gate",
        determinism_level="D_4",
        input_coordinate=input_coord,
        output_coordinate=output_coord,
        monotonic_step=1,
        latency_seconds=0.0
    )
