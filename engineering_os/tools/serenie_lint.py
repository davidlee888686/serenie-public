#!/usr/bin/env python3
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
            frontmatter[k.strip()] = v.strip().strip('"\'')
            
    for key in REQUIRED_KEYS:
        if key not in frontmatter:
            errors.append(f'CHK-DOC-002 FAIL: Missing key {key}')
            
    body = parts[2]
    for vendor in FORBIDDEN_VENDORS:
        if re.search(rf'\b{vendor}\b', body, re.IGNORECASE):
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