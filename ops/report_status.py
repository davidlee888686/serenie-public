import sys
import json
import sqlite3
import hashlib
from pathlib import Path

# Add runtime directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "runtime"))
from storage.cas import DiskCASBackend
from storage.metadata_index import SQLiteMetadataIndex
from repository_intelligence.discovery import SerenieDiscoveryEngine

def main():
    root_dir = Path(__file__).resolve().parent.parent
    print("=================================================================")
    print("         SERENIE SUBSTRATE KERNEL — SYSTEM STATUS DASHBOARD      ")
    print("=================================================================\n")

    # 1. Discovery Audit
    discovery = SerenieDiscoveryEngine(str(root_dir))
    disc_report = discovery.execute_discovery()
    
    # 2. Metadata Index Invariant Check
    db_path = root_dir / "ops" / "cache" / "metadata.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    index = SQLiteMetadataIndex(db_path)
    inv_check = index.verify_invariants()
    index.close()

    # 3. Compile System Status Payload
    status_payload = {
        "system_name": "Serenie Substrate Kernel",
        "version": "1.0.0-FREEZE",
        "status": "OPERATIONAL",
        "scanned_files": disc_report["total_files"],
        "invariants": {
            "inv_sys_005_passed": inv_check["inv_sys_005_passed"],
            "orphaned_edges_count": len(inv_check["orphaned_edges"])
        }
    }

    report_file = root_dir / "ops" / "reports" / "SYSTEM_STATUS.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(status_payload, f, indent=2)

    print(f"[✓] Status: {status_payload['status']}")
    print(f"    -> Version        : {status_payload['version']}")
    print(f"    -> Total Files    : {status_payload['scanned_files']}")
    print(f"    -> INV-SYS-005    : {'PASS' if inv_check['inv_sys_005_passed'] else 'FAIL'}")
    print(f"    -> Report File    : {report_file}")

if __name__ == "__main__":
    main()
