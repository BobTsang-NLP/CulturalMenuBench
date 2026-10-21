#!/usr/bin/env python3
"""Verify SHA256SUMS after downloading archives or extracting the dataset."""

import argparse
import json
from pathlib import Path
import re

from load_dataset import file_digest, relative_file


def verify(directory, checksums="SHA256SUMS"):
    entries = []
    seen = set()
    for line in relative_file(directory, checksums).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        matched = re.fullmatch(r"([0-9a-fA-F]{64}) [ *](.+)", line)
        if matched is None:
            raise ValueError("Malformed SHA256SUMS line")
        checksum, filename = matched.groups()
        path = relative_file(directory, filename)
        if filename in seen:
            raise ValueError("Duplicate checksum filename")
        seen.add(filename)
        entries.append((checksum.lower(), path, filename))
    if not entries:
        raise ValueError("Checksum file is empty")
    failed = []
    for expected, path, filename in entries:
        if not path.is_file() or file_digest(path) != expected:
            failed.append(filename)
    return {"files_checked": len(entries), "failed_files": failed, "passed": not failed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--checksums", default="SHA256SUMS")
    args = parser.parse_args()
    result = verify(args.directory, args.checksums)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
