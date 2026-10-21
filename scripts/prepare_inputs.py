#!/usr/bin/env python3
"""Export ordered model inputs without answers, metadata, model calls or API keys."""

import argparse
import json
from pathlib import Path

from load_dataset import load_media_manifest, model_content, questions


def request_record(question, root, manifest, image_mode="path"):
    return {"item_id": question["item_id"], "task_name": question["task_name"],
            "messages": [{"role": "user", "content": model_content(question, root, manifest, image_mode)}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True,
                        help="Absolute path, or path relative to data-root")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image-mode", choices=("path", "data-url"), default="path")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("limit must be positive")
    manifest = load_media_manifest(args.data_root)
    question_path = args.questions if args.questions.is_absolute() else args.data_root / args.questions
    count = 0
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            for question in questions(question_path, args.limit):
                record = request_record(question, args.data_root, manifest, args.image_mode)
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            if not count:
                raise ValueError("Question file is empty")
    except FileExistsError:
        raise
    except Exception:
        args.output.unlink(missing_ok=True)
        raise
    print(json.dumps({"requests_written": count, "image_mode": args.image_mode, "model_calls": 0}))


if __name__ == "__main__":
    main()
