#!/usr/bin/env python3
"""Strict offline scoring of versioned answer manifests and saved choices."""

import argparse
import json
from pathlib import Path


DOMAINS = {"mc4": {"A", "B", "C", "D"}, "binary": {"是", "否"}}


def normalize(value):
    if not isinstance(value, str):
        raise ValueError("Answers must be strings")
    return value.strip().upper()


def read_rows(path):
    with Path(path).open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    if not rows:
        raise ValueError("Input must not be empty")
    indexed = {}
    for row in rows:
        item_id = row["item_id"]
        if not isinstance(item_id, str) or not item_id:
            raise ValueError("item_id must be a nonempty string")
        if item_id in indexed:
            raise ValueError("Duplicate item_id: " + item_id)
        indexed[item_id] = row
    return indexed


def score(manifest_path, predictions_path):
    manifest = read_rows(manifest_path)
    predictions = read_rows(predictions_path)
    if manifest.keys() != predictions.keys():
        raise ValueError(
            "ID coverage mismatch: missing=%d unexpected=%d"
            % (len(manifest.keys() - predictions.keys()), len(predictions.keys() - manifest.keys()))
        )
    by_task = {}
    invalid = 0
    for item_id, expected in manifest.items():
        prediction = predictions[item_id]
        if expected["task_name"] != prediction["task_name"]:
            raise ValueError("Task mismatch: " + item_id)
        domain = DOMAINS[expected["answer_type"]]
        truth = normalize(expected["ground_truth"])
        answer = normalize(prediction["model_answer"])
        if truth not in domain:
            raise ValueError("Ground truth outside answer domain: " + item_id)
        if answer and answer not in domain:
            raise ValueError("Prediction outside answer domain: " + item_id)
        invalid += not answer
        task = by_task.setdefault(expected["task_name"], {"correct": 0, "total": 0})
        task["total"] += 1
        task["correct"] += int(answer == truth)
    for counts in by_task.values():
        counts["accuracy_percent"] = 100 * counts["correct"] / counts["total"]
    correct = sum(counts["correct"] for counts in by_task.values())
    return {
        "correct": correct,
        "total": len(manifest),
        "accuracy_percent": 100 * correct / len(manifest),
        "empty_incorrect_predictions": invalid,
        "by_task": dict(sorted(by_task.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(score(arguments.manifest, arguments.predictions), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
