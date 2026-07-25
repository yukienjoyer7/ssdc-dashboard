"""Evaluate semantic matching against keyword baseline for sample requests.

Usage:
    uv run python tests/evaluate_matching.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from services.analytical_tables import build_request_table, build_student_profile, _compute_as_of_date, _load_table
from services.semantic_matching import baseline_keyword_score, build_request_text, build_student_text
from config.settings import resolve_data_dir

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "processed" / "evaluation_results"
TOP_K = 10

SAMPLE_REQUESTS = {
    "Data Analyst": ["TR003", "TR008"],
    "Frontend Developer": ["TR055", "TR112"],
    "UI/UX Designer": ["TR081", "TR182"],
    "Business Analyst": ["TR018", "TR089"],
    "Data Entry Operator": ["TR074", "TR092"],
}


def main() -> None:
    data_dir = resolve_data_dir()
    tables = {
        f: _load_table(data_dir, f)
        for f in ["talent_request.csv", "tracking_company.csv", "tracking_student.csv", "status_student.csv", "student_all.csv"]
    }
    as_of = _compute_as_of_date(tables)
    df_req = build_request_table(
        tables["talent_request.csv"], tables["tracking_company.csv"], tables["tracking_student.csv"], as_of
    )
    df_student = build_student_profile(tables["student_all.csv"], tables["status_student.csv"])

    scores = pd.read_parquet(Path(__file__).resolve().parents[1] / "data" / "processed" / "semantic_scores.parquet")
    semantic_metadata = json.loads(
        (Path(__file__).resolve().parents[1] / "data" / "processed" / "semantic_metadata.json").read_text()
    )

    all_request_ids = [req_id for ids in SAMPLE_REQUESTS.values() for req_id in ids]
    per_request_rows: list[dict] = []
    summary_rows: list[dict] = []

    for position_type, request_ids in SAMPLE_REQUESTS.items():
        for request_id in request_ids:
            request_rows = _evaluate_request(
                request_id, position_type, df_req, df_student, scores
            )
            per_request_rows.extend(request_rows)

            semantic_top5 = [r for r in request_rows if r["semantic_rank"] <= 5]
            baseline_ranked = sorted(request_rows, key=lambda r: r["baseline_score"], reverse=True)
            baseline_top5 = baseline_ranked[:5]
            semantic_nims = {r["NIM"] for r in semantic_top5}
            baseline_nims = {r["NIM"] for r in baseline_top5}
            overlap = len(semantic_nims & baseline_nims)
            precision_at_5 = overlap / 5 if semantic_top5 else 0

            semantic_scores = [r["semantic_score"] for r in semantic_top5 if r["semantic_score"] is not None]
            score_spread = max(semantic_scores) - min(semantic_scores) if len(semantic_scores) > 1 else 0

            summary_rows.append({
                "id_talent_req": request_id,
                "position_type": position_type,
                "candidates_evaluated": len(request_rows),
                "precision_at_5": round(precision_at_5, 2),
                "score_spread_top5": round(score_spread, 4),
                "mean_semantic_score": round(
                    sum(s["semantic_score"] for s in request_rows[:5]) / min(5, len(request_rows)), 4
                ),
                "mean_baseline_score": round(
                    sum(s["baseline_score"] for s in request_rows[:5]) / min(5, len(request_rows)), 4
                ),
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    per_request = pd.DataFrame(per_request_rows)
    summary = pd.DataFrame(summary_rows)

    # precision_at_5 comes from overlap count, reassign as float
    summary["precision_at_5"] = summary["precision_at_5"].astype(float)

    per_request.to_csv(OUTPUT_DIR / "per_request_top10.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "summary.csv", index=False)

    _write_review_sheet(per_request, output_dir=OUTPUT_DIR)

    print(f"Results saved to {OUTPUT_DIR}")
    print(f"  per_request_top10.csv: {len(per_request)} rows ({len(df_req[df_req['id_talent_req'].isin(all_request_ids)]['id_talent_req'].unique())} requests)")
    print(f"  summary.csv: {len(summary)} rows")
    print(f"  review_sheet.csv: ready for manual labeling")
    print(f"\nAggregate summary:")
    print(summary.to_string(index=False))


def _evaluate_request(
    request_id: str,
    position_type: str,
    df_req: pd.DataFrame,
    df_student: pd.DataFrame,
    scores: pd.DataFrame,
) -> list[dict]:
    request_rows = df_req.loc[df_req["id_talent_req"] == request_id]
    if request_rows.empty:
        return []
    request = request_rows.iloc[0]
    req_scores = scores.loc[scores["id_talent_req"] == request_id].sort_values("semantic_score", ascending=False).head(TOP_K)
    if req_scores.empty:
        return []

    ranked = req_scores.merge(
        df_student[["NIM", "nama", "program_studi", "semester", "tools_normalized",
                     "bidang_minat", "IPK", "ketersediaan", "status", "CV", "eligible",
                     "jenis_penempatan_diminati", "domisili"]],
        on="NIM",
        how="left",
    )

    rows: list[dict] = []
    for _, student in ranked.iterrows():
        baseline = baseline_keyword_score(request, student)
        rows.append({
            "id_talent_req": request_id,
            "position_type": position_type,
            "NIM": student["NIM"],
            "nama": student.get("nama", ""),
            "program_studi": student.get("program_studi", ""),
            "semester": student.get("semester", ""),
            "IPK": student.get("IPK", ""),
            "tools_normalized": student.get("tools_normalized", ""),
            "bidang_minat": student.get("bidang_minat", ""),
            "ketersediaan": student.get("ketersediaan", ""),
            "domisili": student.get("domisili", ""),
            "jenis_penempatan_diminati": student.get("jenis_penempatan_diminati", ""),
            "status": student.get("status", ""),
            "CV": student.get("CV", ""),
            "eligible": student.get("eligible", ""),
            "semantic_score": student["semantic_score"],
            "semantic_rank": int(student["semantic_rank"]),
            "baseline_score": round(baseline, 4),
            "request_text": build_request_text(request),
            "student_text": build_student_text(student),
        })
    return rows


def _write_review_sheet(per_request: pd.DataFrame, output_dir: Path) -> None:
    review_columns = [
        "id_talent_req", "position_type", "semantic_rank",
        "NIM", "program_studi", "semester", "IPK", "tools_normalized",
        "bidang_minat", "ketersediaan", "domisili",
        "semantic_score", "baseline_score",
        "label_r1", "label_r2", "label_r3",
    ]
    available = [c for c in review_columns if c in per_request.columns]
    review = per_request[available].copy()
    for col in ["label_r1", "label_r2", "label_r3"]:
        if col in review.columns:
            review[col] = review[col].astype(object)
        else:
            review[col] = ""
    review = review.sort_values(["position_type", "id_talent_req", "semantic_rank"])
    review.to_csv(output_dir / "review_sheet.csv", index=False)


if __name__ == "__main__":
    main()
