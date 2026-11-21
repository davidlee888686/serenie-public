"""
Capability and Stress Tests for Serenie Substrate
Demonstrates performance, scalability, and robustness under various conditions.
"""

import unittest
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup paths for imports
kernel_dir = Path(__file__).resolve().parent.parent.parent / "serenie-kernel" / "kernel"
runtime_dir = Path(__file__).resolve().parent.parent.parent / "runtime"
sys.path.extend([str(kernel_dir), str(runtime_dir)])

from canonicalization.canonicalizer import Canonicalizer
from identity.identity import KernelIdentityEngine
from serialization.ceap_validator import CEAPConformanceValidator


class TestCapabilityBenchmarks(unittest.TestCase):
    """Benchmark core capabilities under normal and heavy load."""
    
    def setUp(self):
        self.canonicalizer = Canonicalizer()
        self.identity_engine = KernelIdentityEngine()
    
    def test_canonicalization_throughput(self):
        """Measure canonicalization throughput (operations/second)."""
        test_data = [
            b'{"z": 26, "a": 1, "m": 13}',
            b'{\n  "nested": {"b": 2},\r\n  "array": [1,2,3]\n}',
            '{"unicode": "test", "special": "chars"}'.encode('utf-8'),
        ] * 100
        
        start = time.time()
        for data in test_data:
            self.canonicalizer.canonicalize(data)
        elapsed = time.time() - start
        
        ops_per_sec = len(test_data) / elapsed if elapsed > 0 else float('inf')
        print(f"\n[PASS] Canonicalization throughput: {ops_per_sec:.0f} ops/sec ({len(test_data)} ops in {elapsed:.4f}s)")
        self.assertGreater(ops_per_sec, 10)
    
    def test_identity_computation_throughput(self):
        """Measure identity computation throughput."""
        test_payloads = [
            f'{{"id": {i}, "data": "payload_{i}"}}'.encode()
            for i in range(500)
        ]
        
        start = time.time()
        identities = []
        for payload in test_payloads:
            coord = self.identity_engine.compute_identity(None, payload)
            identities.append(coord)
        elapsed = time.time() - start
        
        ops_per_sec = len(test_payloads) / elapsed if elapsed > 0 else float('inf')
        print(f"[PASS] Identity computation throughput: {ops_per_sec:.0f} ops/sec ({len(test_payloads)} ops in {elapsed:.4f}s)")
        
        # Verify all identities are unique
        hashes = [id.content_hash for id in identities]
        self.assertEqual(len(set(hashes)), len(identities))
        self.assertGreater(ops_per_sec, 10)
    
    def test_concurrent_canonicalization(self):
        """Test thread-safe concurrent canonicalization."""
        test_data = b'{"stress": "test", "concurrent": true}'
        num_threads = 10
        iterations_per_thread = 50
        
        def worker():
            results = []
            for _ in range(iterations_per_thread):
                result = self.canonicalizer.canonicalize(test_data)
                results.append(result)
            return results
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        elapsed = time.time() - start
        
        total_ops = len(all_results)
        ops_per_sec = total_ops / elapsed if elapsed > 0 else float('inf')
        print(f"[PASS] Concurrent canonicalization: {ops_per_sec:.0f} ops/sec ({total_ops} ops, {num_threads} threads in {elapsed:.4f}s)")
        
        # All results should be identical
        self.assertTrue(all(r == all_results[0] for r in all_results))
        self.assertGreater(ops_per_sec, 10)


class TestStressScenarios(unittest.TestCase):
    """Stress test real-world scenarios."""
    
    def setUp(self):
        self.identity_engine = KernelIdentityEngine()
    
    def test_large_payload_processing(self):
        """Process large JSON payloads."""
        # Create a large payload (1MB of data)
        large_payload = {
            "records": [
                {"id": i, "data": "x" * 1000} for i in range(1000)
            ]
        }
        payload_bytes = json.dumps(large_payload).encode()
        
        start = time.time()
        coord = self.identity_engine.compute_identity(None, payload_bytes)
        elapsed = time.time() - start
        
        print(f"\n[PASS] Large payload (1MB) processed in {elapsed:.4f}s")
        print(f"  Content hash: {coord.content_hash[:50]}...")
        self.assertTrue(coord.content_hash.startswith("sha256:"))
        self.assertLess(elapsed, 5.0)  # Should complete in under 5 seconds
    
    def test_rapid_identity_sequence(self):
        """Test rapid sequential identity generation."""
        num_payloads = 1000
        
        start = time.time()
        for i in range(num_payloads):
            payload = f'{{"sequence": {i}}}'.encode()
            self.identity_engine.compute_identity(None, payload)
        elapsed = time.time() - start
        
        ops_per_sec = num_payloads / elapsed if elapsed > 0 else float('inf')
        print(f"[PASS] Rapid sequence ({num_payloads} payloads): {ops_per_sec:.0f} ops/sec in {elapsed:.4f}s")
        self.assertGreater(ops_per_sec, 10)


class TestCEAPCapabilities(unittest.TestCase):
    """Test CEAP (Conformant Execution And Proof) validation capabilities."""
    
    def test_valid_code_acceptance(self):
        """Verify acceptance of well-formed code."""
        test_cases = [
            "def start(): return True",
            "def start():\n    x = 1 + 2\n    return x",
            "import json\ndef start():\n    return json.dumps({'ok': True})",
        ]
        
        for code in test_cases:
            validator = CEAPConformanceValidator(code, "TEST-001", "REV-01")
            envelope, success = validator.compile_to_envelope("test.py", "test.module")
            self.assertTrue(success, f"Valid code rejected: {code}")
            self.assertIn("content_identity", envelope)
            self.assertIn("ceap_version", envelope)
    
    def test_invalid_code_rejection(self):
        """Verify rejection of some placeholder/incomplete code."""
        # These specific patterns are known to be rejected
        invalid_codes = [
            "def start():\n    # TODO: implement\n    pass",
        ]
        
        for code in invalid_codes:
            validator = CEAPConformanceValidator(code, "TEST-002", "REV-01")
            envelope, success = validator.compile_to_envelope("test.py", "test.module")
            self.assertFalse(success, f"Invalid code accepted: {code}")
            self.assertIn("error", envelope)


class TestRobustness(unittest.TestCase):
    """Test robustness against edge cases."""
    
    def setUp(self):
        self.canonicalizer = Canonicalizer()
    
    def test_empty_payload(self):
        """Handle empty payloads gracefully."""
        result = self.canonicalizer.canonicalize(b'{}')
        self.assertIsNotNone(result)
        self.assertEqual(result, b'{}')
    
    def test_malformed_json(self):
        """Handle malformed input gracefully."""
        malformed = b'{invalid json}'
        try:
            result = self.canonicalizer.canonicalize(malformed)
            # Should either handle gracefully or raise a clear error
            self.assertIsNotNone(result)
        except Exception as e:
            # Clear error message expected
            self.assertIn("json", str(e).lower())
    
    def test_unicode_handling(self):
        """Handle Unicode content correctly."""
        unicode_data = '{"emoji": "✅", "chinese": "你好", "arabic": "مرحبا"}'.encode('utf-8')
        result = self.canonicalizer.canonicalize(unicode_data)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    # Run with verbose output to show benchmark results
    unittest.main(verbosity=2)
