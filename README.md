# CulturalMenuBench

**Probing the Knowledge-Application Gap in Multimodal Culinary Reasoning**

[Paper](https://arxiv.org/abs/2609.03526) · [Dataset](https://huggingface.co/datasets/brainz/CulturalMenuBench)

Multimodal culinary questions connecting dish appearance and cooking-process evidence
with dish names, ingredients, preparation, and cuisine knowledge.

This repository is the lightweight code and documentation companion for the
`menubench-data-v3-candidate-20261021` dataset. Images and complete question/answer
files are distributed separately, not committed to this repository.

**Release status:** the v3 dataset is hosted on Hugging Face. Code license, final
citation, data redistribution permissions, and a contact/removal-request channel
still require author confirmation. See [release status](docs/RELEASE_STATUS.md).

## Dataset scope

| Suite | Questions |
|---|---:|
| Binary | 4,870 |
| Chinese multiple-choice | 2,607 |
| Foreign multiple-choice | 3,217 |
| Chinese subregion | 354 |
| **Total** | **11,048** |

587 main dishes; 12,060 image IDs resolving to 12,057 physical images.
The v3 candidate uses reviewed display names and native-resolution JPEG images.
Three download archives total approximately 724 MiB: one metadata ZIP and two image ZIPs.
Download **all three** and extract into the same empty directory; do not concatenate ZIPs.
See [data format](docs/DATA_FORMAT.md), [dataset card](docs/DATA_CARD.md), and
[version notes](docs/VERSION_NOTES.md).

## Quick start

Python 3.9+ and the standard library only. No installation, API keys, network requests,
model inference, or paid API calls are needed to run these tools.
Run commands from the repository root.

### 1. Try the scorer without downloading data

```bash
python3 scripts/score.py \
  --manifest examples/synthetic_manifest.jsonl \
  --predictions examples/synthetic_predictions.jsonl
```

Expected result: 2/3 correct (66.67%). These invented rows are a format demonstration,
not real benchmark examples or paper results.

### 2. Verify downloads and extracted data

Download the three archives from the
[Hugging Face dataset repository](https://huggingface.co/datasets/brainz/CulturalMenuBench).
With the Hugging Face CLI:

```bash
hf download brainz/CulturalMenuBench --repo-type dataset --local-dir downloads
```

The repository root `SHA256SUMS` will be placed in `downloads/` as well. Verify,
then extract:

```bash
python3 scripts/verify_downloads.py --directory downloads
mkdir -p data
for archive in downloads/MenuBench_*_v3_candidate_20261021*.zip; do
  unzip -q "$archive" -d data
done
python3 scripts/verify_downloads.py --directory data
```

The dataset `SHA256SUMS` covers the three ZIPs, `README.md` and `RIGHTS.md`. The
dataset is distributed as archives; the Hugging Face Dataset Viewer and
`datasets.load_dataset` are not supported.

### 3. Validate a question suite

```bash
python3 scripts/load_dataset.py \
  --data-root data --questions questions/mc-chinese.jsonl
```

This checks question/image joins and the byte length and SHA256 of referenced images.
Use `--limit 10` for a quick sample. Repeat for `binary`, `mc-foreign`, and `subregion`
to check the other suites. Full download checksums cover every packaged file.

### 4. Prepare model inputs

```bash
mkdir -p outputs
python3 scripts/prepare_inputs.py \
  --data-root data --questions questions/mc-chinese.jsonl \
  --limit 10 --image-mode path --output outputs/requests.jsonl
```

The exporter preserves the original ordered text/image blocks and includes only
`item_id`, `task_name`, and user `messages`: **no ground-truth answers or recipe metadata**.
`path` mode emits local absolute image paths for your own local-model adapter; these
paths are not remotely accessible URLs. `--image-mode data-url` embeds image bytes as
base64 data URLs, if supported by your chosen API. This is a transport example, not
a provider-specific inference runner or a reproduction of historical model settings.
Never feed the full question row, answer manifests, or recipe metadata to a model.

### 5. Save predictions and score

Your model adapter should save one JSON object per line:

```json
{"item_id":"mc:chinese:0000","task_name":"dish_image2dish_name","model_answer":"C"}
```

The line above illustrates the schema only, not a new model output. Score predictions
for a **complete suite**, matching its IDs and task names:

```bash
python3 scripts/score.py \
  --manifest data/manifests/mc-chinese.jsonl \
  --predictions predictions/mc-chinese.jsonl
```

MC predictions are `A`/`B`/`C`/`D`; binary predictions are `是`/`否`.
Empty answers count as incorrect. Duplicate IDs, missing/extra IDs, task mismatches,
and nonempty out-of-domain answers fail rather than silently changing the denominator.
The scorer trims whitespace and uppercases letters; it does not extract answers from
free-form explanations. Report per-suite and per-task results with the dataset version.
The 10-question input-export example cannot be scored against a complete-suite manifest.

## Included code

- `scripts/load_dataset.py`: joins and validates separately downloaded data.
- `scripts/prepare_inputs.py`: exports ordered answer-free model requests.
- `scripts/score.py`: strict offline scoring, identical to the v3 dataset scorer.
- `scripts/verify_downloads.py`: portable streaming SHA256 verification.
- `tests/`: offline unit and command-line tests using synthetic fixtures.

```bash
python3 -m unittest discover -s tests -v
```

## Citation and permissions

`CITATION.cff` is a carried-forward draft; confirm its author list and final publication
metadata before public release. No new evaluation was performed for v3; historical
paper scores are not measurements of the revised text/JPEG inputs.
See [permissions](LICENSE_PENDING.md). Preprocessing does not grant permission to
redistribute third-party recipe images or text. No open license is granted by this
staging directory, and no absolute watermark-free claim is made.
