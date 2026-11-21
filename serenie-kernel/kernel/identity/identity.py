import hashlib
import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class IdentityCoordinate:
    logical_id: str
    version_id: int
    content_hash: str

    def to_string(self) -> str:
        return f"{self.logical_id}::REV-{self.version_id:03d}::{self.content_hash[:16].upper()}"

class KernelIdentityEngine:
    def logical_identity(self, artifact) -> str:
        if hasattr(artifact, "logical_id") and artifact.logical_id:
            return artifact.logical_id
        return f"ART-{uuid.uuid4().hex[:8].upper()}"

    def version_identity(self, artifact, is_semantic_change: bool = False) -> int:
        if not hasattr(artifact, "version_id"):
            return 1
        if is_semantic_change:
            return artifact.version_id + 1
        return artifact.version_id

    def content_identity(self, canonical_bytes: bytes) -> str:
        return f"sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"

    def compute_identity(self, artifact, canonical_bytes: bytes, is_semantic_change: bool = False) -> IdentityCoordinate:
        logical = self.logical_identity(artifact)
        version = self.version_identity(artifact, is_semantic_change)
        content = self.content_identity(canonical_bytes)
        return IdentityCoordinate(logical, version, content)
