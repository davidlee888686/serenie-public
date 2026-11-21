import os
import sys
from pathlib import Path

def setup():
    dirs = [
        'engineering_os/specification',
        'engineering_os/governance/rfcs',
        'engineering_os/governance/decisions',
        'engineering_os/tools',
        'runtime/repository_intelligence',
        'runtime/provider_manager',
        'runtime/orchestrator',
        'runtime/agent_runtime',
        'runtime/services',
        'tests'
    ]

    print("🚀 Initializing Serenie Engineering OS Repository Structure...")
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"  ├── Created: {d}/")

    # 1. Save serenie_lint.py
    lint_code = """#!/usr/bin/env python3
import sys, re, argparse
from pathlib import Path

REQUIRED_KEYS = ['ID', 'Title', 'Version', 'Status', 'Owner', 'Authority', 'Purpose', 'Scope', 'Dependencies', 'Normative References']
FORBIDDEN_VENDORS = ['Claude', 'GPT-4', 'Hermes', 'Anthropic', 'OpenAI']
RFC_2119_KEYWORDS = ['SHALL', 'SHALL NOT', 'MUST', 'MUST NOT', 'SHOULD', 'SHOULD NOT', 'MAY']

def lint_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f'Read error: {e}']
    
    errors = []
    if not content.startswith('---'):
        return False, ['CHK-DOC-001 FAIL: Frontmatter MUST start with --- on line 1.']
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, ['CHK-DOC-001 FAIL: Unclosed YAML frontmatter.']
    
    frontmatter = {}
    for line in parts[1].strip().splitlines():
        if ':' in line and not line.strip().startswith('#'):
            k, v = line.split(':', 1)
            frontmatter[k.strip()] = v.strip().strip('"\\'')
            
    for key in REQUIRED_KEYS:
        if key not in frontmatter:
            errors.append(f'CHK-DOC-002 FAIL: Missing key {key}')
            
    body = parts[2]
    for vendor in FORBIDDEN_VENDORS:
        if re.search(rf'\\b{vendor}\\b', body, re.IGNORECASE):
            errors.append(f'CHK-DOC-004 FAIL: Vendor string {vendor} found.')
            
    return len(errors) == 0, errors

def main():
    target = Path('engineering_os/specification')
    files = list(target.glob('*.md'))
    total_errors = 0
    print(f'🔍 Running serenie-lint across {len(files)} specification files...')
    for f in files:
        ok, errs = lint_file(f)
        if ok:
            print(f'✅ PASS: {f.name}')
        else:
            print(f'❌ FAIL: {f.name}')
            for e in errs:
                print(f'   └── {e}')
                total_errors += 1
    sys.exit(total_errors)

if __name__ == '__main__':
    main()
"""
    Path('engineering_os/tools/serenie_lint.py').write_text(lint_code.strip(), encoding='utf-8')

    # 2. Write 00_OWNER_MANIFEST.md
    manifest_md = """---
ID: SEOS-000-MANIFEST
Title: Sovereign Owner Manifest & Serenie Substrate Mandate
Version: 1.0.0
Status: Frozen
Owner: Sovereign Owner
Authority: Absolute Sovereign Authority
Purpose: Establishes the immutable vision, product philosophy, non-negotiables, and commercial release goals for Serenie Platform.
Scope: Universal governance across all specifications, runtimes, services, and agent execution environments.
Dependencies: None
Normative References: RFC 2119
---

## 1. Purpose & Core Identity

The Serenie Platform SHALL exist as a sovereign, deterministic, self-consistent engineering substrate. It IS NOT a chat assistant, prompt pack, or ad-hoc automation wrapper.

---

## 2. Non-Negotiable Sovereign Rules

REQ-MAN-001: The system SHALL operate on an offline-first local execution baseline without requiring cloud network sockets for core capabilities.

REQ-MAN-002: Agents operating within the platform SHALL NOT fabricate facts, guess architectural boundaries, or omit explicit evidence.
"""
    Path('engineering_os/specification/00_OWNER_MANIFEST.md').write_text(manifest_md.strip(), encoding='utf-8')

    # 3. Write 01_MASTER_DIRECTIVE.md
    directive_md = """---
ID: SEOS-001-DIRECTIVE
Title: Permanent Master Directive & Serenie Mandate
Version: 1.0.0
Status: Frozen
Owner: Chief Systems Architect / Owner
Authority: Serenie Engineering OS Governing Board
Purpose: Establishes the permanent mandate, workflow rules, quality expectations, and verification requirements.
Scope: All manual and autonomous development across all project tracks.
Dependencies: SEOS-000-MANIFEST
Normative References: RFC 2119
---

## 1. Permanent Engineering Mandate

The platform SHALL enforce enterprise-grade quality across all software artifacts.

REQ-DIR-001: The execution agent SHALL inspect existing repository files, AST nodes, and dependency graphs prior to modifying any code.
"""
    Path('engineering_os/specification/01_MASTER_DIRECTIVE.md').write_text(directive_md.strip(), encoding='utf-8')

    print("\n✨ Initialization complete! Running linter verification...\n")

if __name__ == "__main__":
    setup()
