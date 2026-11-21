import os
import hashlib
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class ArtifactDescriptor:
    artifact_id: str
    kind: str
    content_hash: str
    byte_size: int

class DiskCASBackend:
    def __init__(self, cache_root: Path):
        self.artifacts_dir = cache_root.resolve() / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, c_hash: str) -> Tuple[Path, Path]:
        shard_dir = self.artifacts_dir / c_hash[:2]
        blob_path = shard_dir / f"{c_hash[2:]}.art"
        return shard_dir, blob_path

    def put(self, descriptor: ArtifactDescriptor, payload_bytes: bytes) -> bool:
        actual_hash = hashlib.sha256(payload_bytes).hexdigest()
        if actual_hash != descriptor.content_hash:
            raise ValueError(f"Hash Mismatch! Expected {descriptor.content_hash}, got {actual_hash}")
        
        shard_dir, blob_path = self._get_path(actual_hash)
        if blob_path.exists():
            return False
        
        shard_dir.mkdir(parents=True, exist_ok=True)
        temp_fd, temp_path_str = tempfile.mkstemp(dir=str(shard_dir), prefix=".tmp_art_")
        temp_path = Path(temp_path_str)
        
        try:
            with os.fdopen(temp_fd, "wb") as f:
                f.write(payload_bytes)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, blob_path)
            return True
        except Exception as e:
            if temp_path.exists():
                os.unlink(temp_path)
            raise IOError(f"CAS Write Failed: {e}")

    def get(self, content_hash: str) -> Optional[bytes]:
        _, blob_path = self._get_path(content_hash)
        if not blob_path.exists():
            return None
        data = blob_path.read_bytes()
        if hashlib.sha256(data).hexdigest() != content_hash:
            blob_path.unlink(missing_ok=True)
            return None
        return data
