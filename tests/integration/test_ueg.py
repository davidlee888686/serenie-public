import unittest
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from storage.metadata_index import SQLiteMetadataIndex

class TestMetadataIndex(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "metadata.db"
        self.index = SQLiteMetadataIndex(self.db_path)

    def tearDown(self):
        self.index.close()
        shutil.rmtree(self.temp_dir)

    def test_record_and_verify_invariants(self):
        self.index.record_artifact("ART-001", "sha256:abc123", "PythonModule", 100)
        self.index.record_artifact("ART-002", "sha256:def456", "PythonModule", 200, ["sha256:abc123"])

        result = self.index.verify_invariants()
        self.assertTrue(result["inv_sys_005_passed"])

if __name__ == "__main__":
    unittest.main()
