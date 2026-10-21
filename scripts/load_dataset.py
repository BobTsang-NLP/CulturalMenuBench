#!/usr/bin/env python3
"""Load and validate a separately downloaded CulturalMenuBench dataset."""

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath


DOMAINS = {"mc4": {"A", "B", "C", "D"}, "binary": {"是", "否"}}


def relative_file(root, relative):
    path = PurePosixPath(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError("Unsafe relative path")
    candidate = Path(root) / relative
    candidate.resolve().relative_to(Path(root).resolve())
    return candidate


def file_digest(path):
    checksum = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def rows(path):
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def load_media_manifest(root):
    manifest = {}
    for entry in rows(Path(root) / "media_manifest.jsonl"):
        image_id = entry["image_id"]
        if not isinstance(image_id, str) or not image_id or image_id in manifest:
            raise ValueError("Invalid or duplicate image ID")
        relative_file(root, entry["package_path"])
        manifest[image_id] = entry
    return manifest


def questions(path, limit=None):
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")
    seen = set()
    for number, question in enumerate(rows(path)):
        if limit is not None and number >= limit:
            break
        item_id = question["item_id"]
        if not isinstance(item_id, str) or not item_id or item_id in seen:
            raise ValueError("Invalid or duplicate question ID")
        seen.add(item_id)
        if question["ground_truth"] not in DOMAINS[question["answer_type"]]:
            raise ValueError("Invalid ground truth")
        if not question["input"]:
            raise ValueError("Empty question input")
        yield question


def image_entry(block, manifest):
    reference = block["image_url"]["url"]
    if not reference.startswith("asset://"):
        raise ValueError("Expected asset:// image reference")
    return manifest[reference[len("asset://"):]]


def model_content(question, root, manifest, image_mode="path"):
    if image_mode not in {"path", "data-url"}:
        raise ValueError("Unknown image mode")
    content = []
    for original in question["input"]:
        block = copy.deepcopy(original)
        if block["type"] == "text":
            if not isinstance(block["text"], str):
                raise ValueError("Text input must be a string")
        elif block["type"] == "image_url":
            entry = image_entry(block, manifest)
            path = relative_file(root, entry["package_path"])
            if not path.is_file():
                raise FileNotFoundError(entry["package_path"])
            if image_mode == "data-url":
                mime = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}[entry["format"]]
                encoded = base64.b64encode(path.read_bytes()).decode("ascii")
                block["image_url"]["url"] = "data:" + mime + ";base64," + encoded
            else:
                block["image_url"]["url"] = str(path.resolve())
        else:
            raise ValueError("Unsupported input block type")
        content.append(block)
    return content


def validate(root, question_path, limit=None):
    manifest = load_media_manifest(root)
    checked = set()
    failures = []
    total = 0
    for question in questions(question_path, limit):
        total += 1
        for block in question["input"]:
            if block["type"] == "text":
                if not isinstance(block["text"], str):
                    raise ValueError("Text input must be a string")
                continue
            if block["type"] != "image_url":
                raise ValueError("Unsupported input block type")
            entry = image_entry(block, manifest)
            image_id = entry["image_id"]
            if image_id in checked:
                continue
            checked.add(image_id)
            path = relative_file(root, entry["package_path"])
            try:
                if path.stat().st_size != entry["bytes"] or file_digest(path) != entry["sha256"]:
                    raise ValueError("Image integrity mismatch")
            except (OSError, ValueError) as error:
                failures.append({"image_id": image_id, "error_type": type(error).__name__})
    if not total:
        raise ValueError("Question file is empty")
    return {"questions_checked": total, "unique_images_checked": len(checked),
            "failed_images": len(failures), "failures": failures[:20], "model_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True,
                        help="Absolute path, or path relative to data-root")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("limit must be positive")
    question_path = args.questions if args.questions.is_absolute() else args.data_root / args.questions
    result = validate(args.data_root, question_path, args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["failed_images"] else 0)


if __name__ == "__main__":
    main()
