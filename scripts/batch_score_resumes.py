#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path

from score_resume import load_json, review_resume


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def summarize_hits(items, key):
    values = []
    for item in items:
        value = item.get(key, "")
        if value:
            values.append(value)
    return " | ".join(values)


def main():
    parser = argparse.ArgumentParser(
        description="Batch score extracted resume JSON files and export a ranking CSV."
    )
    parser.add_argument(
        "--input-dir",
        default="output/extracted",
        help="Directory containing extracted candidate JSON files",
    )
    parser.add_argument(
        "--output-dir",
        default="output/scored",
        help="Directory for per-candidate score JSON files",
    )
    parser.add_argument(
        "--rules",
        default="rules/recruiting_rules.json",
        help="Path to recruiting rules JSON",
    )
    parser.add_argument(
        "--ranking-csv",
        default="output/scored/ranking.csv",
        help="Path for the summary ranking CSV",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    ranking_csv = Path(args.ranking_csv)

    ensure_dir(output_dir)
    ensure_dir(ranking_csv.parent)

    rules = load_json(args.rules)
    extracted_files = sorted(input_dir.glob("*.json"))
    rows = []

    for extracted_path in extracted_files:
        candidate = load_json(extracted_path)
        result = review_resume(candidate, rules)
        output_path = output_dir / f"{extracted_path.stem}_score.json"
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        rows.append(
            {
                "file": extracted_path.name,
                "candidate_name": result.get("candidate_name", ""),
                "total_score": result["total_score"],
                "decision": result["decision"],
                "academic_score": result["academic_score"],
                "scholarship_score": result["scholarship_score"],
                "competition_score": result["competition_score"],
                "internship_project_score": result["internship_project_score"],
                "fit_score": result["fit_score"],
                "competition_hits": summarize_hits(result.get("competition_tier_hits", []), "normalized_name"),
                "scholarship_hits": summarize_hits(result.get("scholarship_hits", []), "name"),
                "strengths": " | ".join(result.get("strengths", [])),
                "risks": " | ".join(result.get("risks", [])),
            }
        )

    rows.sort(key=lambda row: (-row["total_score"], row["candidate_name"], row["file"]))

    with ranking_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "file",
                "candidate_name",
                "total_score",
                "decision",
                "academic_score",
                "scholarship_score",
                "competition_score",
                "internship_project_score",
                "fit_score",
                "competition_hits",
                "scholarship_hits",
                "strengths",
                "risks",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Scored {len(rows)} extracted resumes.")
    print(f"Per-candidate results: {output_dir}")
    print(f"Ranking CSV: {ranking_csv}")


if __name__ == "__main__":
    main()
