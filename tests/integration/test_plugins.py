import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from runtime.plugins.plugin_host import PluginCommunicationHost

class TestPluginHost(unittest.TestCase):
    def setUp(self):
        self.host = PluginCommunicationHost("PLUG-001")

    def test_handshake_and_signature_verification(self):
        handshake = self.host.execute_handshake()
        self.assertEqual(handshake["jsonrpc"], "2.0")
        self.assertTrue(self.host.verify_incoming_frame(handshake))

if __name__ == "__main__":
    unittest.main()
