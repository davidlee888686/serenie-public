import sys
import json
from pathlib import Path

# Add runtime directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "runtime"))
from repository_intelligence.discovery import SerenieDiscoveryEngine

def main():
    root_dir = Path(__file__).resolve().parent.parent
    print(f"[*] Running Phase 00 Discovery against repository: {root_dir}")
    
    engine = SerenieDiscoveryEngine(str(root_dir))
    report = engine.execute_discovery()
    
    output_path = root_dir / "ops" / "reports" / "PHASE_00_REPORT.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"[✓] Discovery complete. Total files scanned: {report['total_files']}")
    print(f"    -> Report saved to: {output_path}")

if __name__ == "__main__":
    main()
