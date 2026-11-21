import unittest
import sys
from pathlib import Path

# Add serenie-kernel/kernel to sys.path
kernel_dir = Path(__file__).resolve().parent.parent.parent / "serenie-kernel" / "kernel"
sys.path.append(str(kernel_dir))

from canonicalization.canonicalizer import Canonicalizer
from identity.identity import KernelIdentityEngine

class TestStage1Foundation(unittest.TestCase):
    def setUp(self):
        self.canonicalizer = Canonicalizer()
        self.identity_engine = KernelIdentityEngine()

    def test_canonicalization_idempotence(self):
        raw_data = b'{\n  "b": 2,\r\n  "a": 1\n}'
        pass1 = self.canonicalizer.canonicalize(raw_data)
        pass2 = self.canonicalizer.canonicalize(pass1)
        self.assertEqual(pass1, pass2)

    def test_identity_coordinate_computation(self):
        canonical_bytes = b'{"a":1,"b":2}'
        coord = self.identity_engine.compute_identity(None, canonical_bytes)
        self.assertEqual(coord.version_id, 1)
        self.assertTrue(coord.content_hash.startswith("sha256:"))

if __name__ == "__main__":
    unittest.main()
