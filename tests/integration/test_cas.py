import unittest
import hashlib
import tempfile
import shutil
import sys
from pathlib import Path

# Navigate up three levels: test_cas.py -> integration -> tests -> Serenie
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from storage.cas import DiskCASBackend, ArtifactDescriptor

class TestCASBackend(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cas = DiskCASBackend(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_cas_put_get(self):
        payload = b"print('Serenie Verification Pass')"
        c_hash = hashlib.sha256(payload).hexdigest()
        desc = ArtifactDescriptor("ART-001", "PythonModule", c_hash, len(payload))
        
        stored = self.cas.put(desc, payload)
        self.assertTrue(stored)
        
        retrieved = self.cas.get(c_hash)
        self.assertEqual(retrieved, payload)

if __name__ == "__main__":
    unittest.main()
