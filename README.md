# CulturalMenuBench

**Probing the Knowledge-Application Gap in Multimodal Culinary Reasoning**

**Accepted to Findings of EMNLP 2026.**

📄 **[Paper (arXiv)](https://arxiv.org/abs/2609.03526)** · **[PDF](https://arxiv.org/pdf/2609.03526)**

A multimodal culinary benchmark connecting dish appearance and cooking-process
evidence with dish names, ingredients, preparation, and cuisine knowledge.

## Release status

The data v3 candidate has been prepared locally. Public dataset download links
will be added here when available. This repository contains the companion tools;
it does not yet provide a public dataset download or new evaluation results.

## Dataset

| Suite | Questions |
|---|---:|
| Binary | 4,870 |
| Chinese multiple-choice | 2,607 |
| Foreign multiple-choice | 3,217 |
| Chinese subregion | 354 |
| **Total** | **11,048** |

The candidate contains 587 main dishes and 12,060 image IDs resolving to 12,057
physical images. Reviewed display names and native-resolution JPEG images are
packaged in one metadata ZIP and two image ZIPs, approximately 724 MiB in total.
Download all three archives when published and extract them into the same empty
`data/` directory; do not concatenate ZIPs.

## Requirements

Python 3.9+ and the standard library only. These tools do not call models or APIs.
Run the following commands from the repository root after downloading the data.

## Verify and load

```bash
python3 scripts/verify_downloads.py --directory data
python3 scripts/load_dataset.py \
  --data-root data --questions questions/mc-chinese.jsonl
```

Use `binary`, `mc-foreign`, or `subregion` in place of `mc-chinese` for other suites.
Image IDs must be resolved through `media_manifest.jsonl`, not guessed filenames.

## Prepare model inputs

```bash
mkdir -p outputs
python3 scripts/prepare_inputs.py \
  --data-root data --questions questions/mc-chinese.jsonl \
  --limit 10 --image-mode path --output outputs/requests.jsonl
```

The exporter preserves text/image ordering and outputs question IDs, task names,
and user messages only, without ground-truth answers or recipe metadata. It does
not run inference. Adapt the messages to your chosen model and save its predictions.
`path` mode emits local absolute image paths, not remotely accessible URLs.
`--image-mode data-url` embeds images as base64 for APIs that support this format.
Never send whole question records, answer manifests or recipe metadata to a model.

## Save and score predictions

Save one JSON object per question in a prediction JSONL file. Required fields are
`item_id`, `task_name`, and `model_answer`. For example, the following is an invented
format example, not a benchmark prediction:

```json
{"item_id":"synthetic:example","task_name":"synthetic_mc","model_answer":"A"}
```

For actual evaluation, preserve the dataset's exact IDs and task names. MC answers
must be `A`, `B`, `C`, or `D`; binary answers must be `是` or `否`.

```bash
python3 scripts/score.py \
  --manifest data/manifests/mc-chinese.jsonl \
  --predictions outputs/mc-chinese_predictions.jsonl
```

Predictions must cover the complete suite. A 10-question export is only a smoke test
and cannot be scored against a full-suite manifest. Empty answers count as incorrect;
missing/extra IDs, duplicate IDs, task mismatches and nonempty out-of-domain answers
fail validation. The scorer trims whitespace and uppercases letters, but does not
extract answers from explanations. Report suite/task scores with the dataset version.

## Version and limitations

Version: `menubench-data-v3-candidate-20261021`. Display-name cleanup and JPEG encoding
do not change question IDs, answer labels, option order or image order. Raw webpage
titles remain in source metadata for provenance; use `canonical_name_zh` for reviewed
Chinese display names. No super-resolution or new evaluation was performed.
Historical paper scores are not fresh measurements of these revised inputs.

The package retains known annotation/scope issues; consult `KNOWN_ISSUES.jsonl`.
Inherited image cleaning may estimate hidden pixels, and residual overlays may remain.
The tools do not certify semantic correctness or a completely watermark-free dataset.

## License and data permissions

Repository code is covered by the existing Apache-2.0 `LICENSE`.
This code license does not grant rights to third-party recipe photographs or text.
Dataset permissions, source attribution and a removal-request channel must be
finalized before public dataset distribution. For the current paper citation,
see the arXiv entry linked above.
