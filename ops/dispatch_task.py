import sys
import json
import time
import argparse
from pathlib import Path

# Add runtime directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "runtime"))
from provider_manager.manager import ProviderManager, LLMTask

def main():
    parser = argparse.ArgumentParser(description="Serenie Substrate Task Dispatcher")
    parser.add_argument("--prompt", required=True, help="Task prompt string")
    parser.add_argument("--type", default="coding", choices=["coding", "reasoning", "fast_chat"], help="Task capability type")
    args = parser.parse_args()

    manager = ProviderManager()
    task = LLMTask(task_id=f"TASK-{int(time.time())}", prompt=args.prompt, task_type=args.type)
    
    result = manager.dispatch(task)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
