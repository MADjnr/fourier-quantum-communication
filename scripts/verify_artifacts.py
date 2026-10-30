#!/usr/bin/env python3
"""Verify every archived artifact against the published manifest (stdlib only)."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1] / 'results'
    manifest = json.loads((root / 'manifest.json').read_text())
    errors = []
    for name, expected in manifest['artifacts'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()):
            errors.append(f'Unsafe path: {name}')
            continue
        if not path.is_file():
            errors.append(f'Missing: {name}')
            continue
        data = path.read_bytes()
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            errors.append(f'Mismatch: {name}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f"PASS: {len(manifest['artifacts'])} archived artifacts match their recorded byte counts and SHA-256 hashes.")


if __name__ == '__main__':
    main()
