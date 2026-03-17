#!/usr/bin/env python3

import argparse
import shutil
import json
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Score one local resume batch and export compact results.")
    parser.add_argument(
        "--batch-name",
        required=True,
        help="Batch folder name under resume/ and output/, for example spring-2026-local-01",
    )
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Project root containing rules/ and scripts/",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    batch_name = args.batch_name
    resume_dir = project_root / "resume" / batch_name
    final_output_dir = project_root / "output" / batch_name
    extracted_dir = final_output_dir / ".extracted"
    temp_scored_dir = final_output_dir / ".scored_tmp"
    ranking_csv = final_output_dir / "ranking.csv"
    rules = project_root / "rules" / "recruiting_rules.json"

    if not resume_dir.exists():
        raise SystemExit(f"Resume batch not found: {resume_dir}")

    if not extracted_dir.exists():
        raise SystemExit(f"Extracted directory not found: {extracted_dir}")

    if not any(extracted_dir.glob("*.json")):
        raise SystemExit(f"No extracted JSON files found in: {extracted_dir}")

    final_output_dir.mkdir(parents=True, exist_ok=True)
    temp_scored_dir.mkdir(parents=True, exist_ok=True)
    for old_json in final_output_dir.glob("*.json"):
        old_json.unlink()
    ranking_csv.unlink(missing_ok=True)

    run(
        [
            sys.executable,
            "scripts/batch_score_resumes.py",
            "--input-dir",
            str(extracted_dir),
            "--output-dir",
            str(temp_scored_dir),
            "--rules",
            str(rules),
            "--ranking-csv",
            str(ranking_csv),
        ],
        cwd=project_root,
    )

    for score_file in temp_scored_dir.glob("*_score.json"):
        score_data = load_json(score_file)
        candidate_name = score_data.get("candidate_name") or score_file.stem.replace("_score", "")
        output_path = final_output_dir / f"{candidate_name}.json"
        output_path.write_text(
            json.dumps(score_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        score_file.unlink()

    temp_scored_dir.rmdir()
    shutil.rmtree(extracted_dir)

    print(f"Processed local batch: {batch_name}")
    print(f"Resume dir: {resume_dir}")
    print(f"Ranking CSV: {ranking_csv}")
    print(f"Results: {final_output_dir}")


if __name__ == "__main__":
    main()
