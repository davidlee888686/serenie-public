import sys
import os
import json
import zipfile
import hashlib
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    print("=================================================================")
    print("      SERENIE SUBSTRATE KERNEL — ONE-CLICK RELEASE BUILDER       ")
    print("=================================================================\n")

    # 1. Run CI Tests
    print("[*] Step 1/4: Running CI Test Suite...")
    ci_res = subprocess.run([sys.executable, str(root_dir / "ops" / "run_ci.py")], check=False)
    if ci_res.returncode != 0:
        print("[FATAL] CI Test Suite failed. Aborting release build.", file=sys.stderr)
        sys.exit(1)

    # 2. Compile Specification Traceability
    print("\n[*] Step 2/4: Compiling Specification Traceability...")
    subprocess.run([sys.executable, str(root_dir / "ops" / "compile_spec.py")], check=True)

    # 3. Generate System Status Report
    print("\n[*] Step 3/4: Generating System Status Report...")
    subprocess.run([sys.executable, str(root_dir / "ops" / "report_status.py")], check=True)

    # 4. Package Release ZIP
    print("\n[*] Step 4/4: Packaging Production Release Archive...")
    zip_path = dist_dir / "serenie_substrate_v1.0.0_release.zip"
    
    files_to_pack = [
        "serenie_cli.py",
        "bootstrap.py",
        "runtime/storage/cas.py",
        "runtime/storage/metadata_index.py",
        "runtime/provider_manager/manager.py",
        "runtime/dtr/serenie_substrate.py",
        "runtime/serialization/ceap_validator.py",
        "runtime/repository_intelligence/discovery.py",
        "runtime/plugins/plugin_host.py",
        "engineering_os/specification/00_OWNER_MANIFEST.md",
        "engineering_os/specification/14_SYSTEM_INVARIANTS.md",
        "engineering_os/governance/decisions/ADR_INDEX.md",
        "ops/reports/SYSTEM_STATUS.json",
        "ops/reports/SPECIFICATION_TRACEABILITY.json"
    ]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for rel_str in files_to_pack:
            abs_p = root_dir / rel_str
            if abs_p.exists():
                zipf.write(abs_p, arcname=rel_str)

    zip_bytes = zip_path.read_bytes()
    release_sha256 = hashlib.sha256(zip_bytes).hexdigest()

    release_manifest = {
        "release_name": "Serenie Substrate Kernel",
        "version": "1.0.0-FREEZE",
        "archive_file": str(zip_path.relative_to(root_dir)),
        "archive_size_bytes": len(zip_bytes),
        "sha256_canonical": release_sha256
    }

    manifest_path = dist_dir / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(release_manifest, indent=2), encoding="utf-8")

    print(f"\n[✓] Release Packaging Complete:")
    print(f"    -> Release Zip  : {zip_path}")
    print(f"    -> Size         : {len(zip_bytes)} bytes")
    print(f"    -> SHA-256      : {release_sha256}")
    print(f"    -> Manifest     : {manifest_path}")

if __name__ == "__main__":
    main()
