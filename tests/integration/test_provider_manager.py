import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from provider_manager.manager import ProviderManager, LLMTask

class TestProviderManager(unittest.TestCase):
    def setUp(self):
        self.manager = ProviderManager()

    def test_dispatch_coding_task(self):
        task = LLMTask(task_id="TASK-001", prompt="Implement AST parser", task_type="coding")
        result = self.manager.dispatch(task)
        
        self.assertIn("status", result)
        self.assertIn("provider", result)

    def test_circuit_breaker_failover(self):
        # Trip OpenRouter_Free_Primary with simulated credit errors
        for _ in range(3):
            self.manager.breaker.record_failure("OpenRouter_Free_Primary", "HTTP 402 Out of Credits")
            
        task = LLMTask(task_id="TASK-002", prompt="Analyze invariants", task_type="coding")
        result = self.manager.dispatch(task)
        
        # Verify failover away from unhealthy provider
        self.assertNotEqual(result["provider"], "OpenRouter_Free_Primary")

if __name__ == "__main__":
    unittest.main()
