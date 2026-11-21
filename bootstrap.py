import os
from pathlib import Path

directories = [
    "engineering_os/specification",
    "engineering_os/governance",
    "runtime/provider_manager",
    "runtime/storage",
    "runtime/dtr",
    "tests/integration",
    "tests/golden_corpus",
    "ops/reports"
]

for folder in directories:
    Path(folder).mkdir(parents=True, exist_ok=True)

print("Workspace directory structure initialized.")
