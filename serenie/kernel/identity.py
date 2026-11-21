"""
Serenie Kernel - Identity Subsystem
100% deterministic coordinate identity derivation. Zero non-deterministic randomness.
"""

import json
import hashlib
from dataclasses import dataclass
from typing import Dict, Any, Union

@dataclass(frozen=True)
class IdentityCoordinate:
    logical_id: str
    version_id: Union[int, str]
    content_hash: str

    def to_coordinate_string(self) -> str:
        ver_str = f"REV-{self.version_id:03d}" if isinstance(self.version_id, int) else str(self.version_id)
        hash_short = self.content_hash.replace("sha256:", "")[:16].upper()
        return f"{self.logical_id}::{ver_str}::{hash_short}"

    def to_string(self) -> str:
        return self.to_coordinate_string()

CoordinateIdentity = IdentityCoordinate

class KernelIdentityEngine:
    @staticmethod
    def derive_logical_id(artifact_name: str, payload_bytes: bytes) -> str:
        seed = f"{artifact_name}:{hashlib.sha256(payload_bytes).hexdigest()}".encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()[:8].upper()
        return f"ART-{digest}"

    def logical_identity(self, artifact, default_name: str = "ARTIFACT") -> str:
        if hasattr(artifact, "logical_id") and getattr(artifact, "logical_id"):
            return getattr(artifact, "logical_id")
        if isinstance(artifact, dict) and artifact.get("logical_id"):
            return artifact["logical_id"]
        
        content = str(artifact).encode("utf-8")
        return KernelIdentityEngine.derive_logical_id(default_name, content)

    def version_identity(self, artifact, is_semantic_change: bool = False) -> int:
        current = 1
        if hasattr(artifact, "version_id"):
            val = getattr(artifact, "version_id")
            if isinstance(val, int):
                current = val
        elif isinstance(artifact, dict) and isinstance(artifact.get("version_id"), int):
            current = artifact["version_id"]
            
        if is_semantic_change:
            return current + 1
        return current

    def content_identity(self, canonical_bytes: bytes) -> str:
        return f"sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"

    def compute_identity(
        self, 
        logical_id: str, 
        version_id: Union[int, str], 
        canonical_bytes: bytes
    ) -> IdentityCoordinate:
        content_hash = self.content_identity(canonical_bytes)
        return IdentityCoordinate(
            logical_id=logical_id,
            version_id=version_id,
            content_hash=content_hash
        )

class IdentityEngine:
    @staticmethod
    def derive_coordinate(
        logical_id: str, 
        version_id: Union[int, str], 
        payload: Dict[str, Any]
    ) -> IdentityCoordinate:
        canonical_bytes = json.dumps(
            payload, 
            sort_keys=True, 
            ensure_ascii=False,
            separators=(',', ':')
        ).replace("\r\n", "\n").encode('utf-8')
        
        content_hash = hashlib.sha256(canonical_bytes).hexdigest()
        return IdentityCoordinate(
            logical_id=logical_id,
            version_id=version_id,
            content_hash=content_hash
        )

def compute_identity(
    logical_id: str, 
    version_id: Union[int, str], 
    canonical_bytes: bytes
) -> IdentityCoordinate:
    engine = KernelIdentityEngine()
    return engine.compute_identity(logical_id, version_id, canonical_bytes)
