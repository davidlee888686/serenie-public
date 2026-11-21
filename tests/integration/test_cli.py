import unittest
import sys
import tempfile
import shutil
import os
from pathlib import Path

# Add project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from serenie_cli import SerenieCLI

class TestSerenieCLI(unittest.TestCase):
    def setUp(self):
        self.cli = SerenieCLI()
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_cli_ingest_and_verify(self):
        test_file = self.temp_dir / "sample.py"
        test_file.write_text("import os\ndef run(): return True\n", encoding="utf-8")

        res_ingest = self.cli.run(["ingest", "--file", str(test_file)])
        self.assertEqual(res_ingest, 0)

        res_verify = self.cli.run(["verify"])
        self.assertEqual(res_verify, 0)

    def test_cli_placeholder_rejection(self):
        test_file = self.temp_dir / "bad_sample.py"
        test_file.write_text("# TODO: fix this\ndef run(): pass\n", encoding="utf-8")

        res_ingest = self.cli.run(["ingest", "--file", str(test_file)])
        self.assertEqual(res_ingest, 1)

if __name__ == "__main__":
    unittest.main()
