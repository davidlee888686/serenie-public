import unittest
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from repository_intelligence.discovery import SerenieDiscoveryEngine

class TestDiscoveryEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_discovery_scan(self):
        (self.temp_dir / "sample.py").write_text("def run(): return True\n", encoding="utf-8")
        (self.temp_dir / "doc.md").write_text("# Title\nDocumentation\n", encoding="utf-8")

        engine = SerenieDiscoveryEngine(str(self.temp_dir))
        report = engine.execute_discovery()

        self.assertEqual(report["total_files"], 2)
        self.assertEqual(len(report["files"]), 2)

if __name__ == "__main__":
    unittest.main()
