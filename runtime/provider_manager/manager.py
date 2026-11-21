import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class LLMTask:
    task_id: str
    prompt: str
    task_type: str = "coding"

class CircuitBreaker:
    def __init__(self, threshold: int = 3, cooldown_sec: float = 60.0):
        self.threshold = threshold
        self.cooldown_sec = cooldown_sec
        self.failures: Dict[str, int] = {}
        self.last_failure: Dict[str, float] = {}

    def is_healthy(self, provider_id: str) -> bool:
        if self.failures.get(provider_id, 0) >= self.threshold:
            if time.time() - self.last_failure.get(provider_id, 0) > self.cooldown_sec:
                return True
            return False
        return True

    def record_success(self, provider_id: str):
        self.failures[provider_id] = 0

    def record_failure(self, provider_id: str, reason: str):
        self.failures[provider_id] = self.failures.get(provider_id, 0) + 1
        self.last_failure[provider_id] = time.time()
        logging.warning(f"CircuitBreaker: '{provider_id}' failed ({reason}). Count: {self.failures[provider_id]}")

class ProviderManager:
    LADDER = [
        {"id": "OpenRouter_Free_Primary", "model": "qwen/qwen-2.5-coder-32b-instruct:free", "type": "cloud_free", "task": "coding"},
        {"id": "OpenRouter_Free_Reasoning", "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "type": "cloud_free", "task": "reasoning"},
        {"id": "Local_Ollama", "model": "qwen2.5-coder:32b", "type": "local", "task": "coding"},
        {"id": "Offline_Fallback", "model": "offline-rule-engine", "type": "offline", "task": "all"}
    ]

    def __init__(self):
        self.breaker = CircuitBreaker()

    def dispatch(self, task: LLMTask) -> Dict[str, Any]:
        for candidate in self.LADDER:
            pid = candidate["id"]
            if (candidate["task"] == task.task_type or candidate["task"] == "all") and self.breaker.is_healthy(pid):
                return {
                    "task_id": task.task_id,
                    "provider": pid,
                    "model": candidate["model"],
                    "status": "DISPATCHED",
                    "type": candidate["type"]
                }
        return {
            "task_id": task.task_id,
            "provider": "Offline_Fallback",
            "model": "offline-rule-engine",
            "status": "OFFLINE_MODE",
            "type": "offline"
        }
