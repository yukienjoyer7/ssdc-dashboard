"""Semantic talent matching pipeline using Qwen3-Embedding-0.6B.

Precomputes semantic relevance scores for all request–student pairs and
saves them as Parquet for the dashboard to consume at runtime.

Usage:
    from services.semantic_matching import build_all
    metadata = build_all()
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
TOP_K = 10
BATCH_SIZE = 64
_PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def _safe(value: Any, default: str = "Tidak tersedia") -> str:
    if pd.isna(value) or str(value).strip().lower() in ("", "nan", "none"):
        return default
    return str(value).strip()


def build_request_text(row: pd.Series) -> str:
    return (
        f"Posisi: {_safe(row.get('nama_posisi'))}.\n"
        f"Bidang studi: {_safe(row.get('bidang_studi_dibutuhkan_normalized'))}.\n"
        f"Jenis penempatan: {_safe(row.get('jenis_penempatan'))}.\n"
        f"Skema kerja: {_safe(row.get('working_arrangement'))}.\n"
        f"Requirement: {_safe(row.get('deskripsi_requirement'))}."
    )


def build_student_text(row: pd.Series) -> str:
    return (
        f"Program studi: {_safe(row.get('program_studi'))}.\n"
        f"Bidang minat: {_safe(row.get('bidang_minat'))}.\n"
        f"Tools dan kompetensi: {_safe(row.get('tools_normalized'))}.\n"
        f"Preferensi penempatan: {_safe(row.get('jenis_penempatan_diminati'))}."
    )


def _tokenize_keywords(text: str) -> set[str]:
    cleaned = re.sub(r"[()]", " ", str(text).lower())
    parts = re.split(r"[,;]+", cleaned)
    result: set[str] = set()
    for part in parts:
        for sub in re.split(r"/", part):
            for word in re.split(r"\s+", sub.strip()):
                word = word.strip(".-")
                if len(word) >= 2 and word not in (
                    "", "nan", "none", "dan", "serta", "atau", "yang", "dengan",
                    "mampu", "dasar", "dalam", "baik", "menguasai",
                ):
                    result.add(word)
    return result


def baseline_keyword_score(request: pd.Series, student: pd.Series) -> float:
    req_keywords = _tokenize_keywords(
        str(request.get("bidang_studi_dibutuhkan_normalized", ""))
        + " "
        + str(request.get("deskripsi_requirement", ""))
    )
    student_tools = _tokenize_keywords(str(student.get("tools_normalized", "")))
    if not req_keywords or not student_tools:
        return 0.0
    overlap = len(req_keywords & student_tools)
    return overlap / max(len(req_keywords), len(student_tools))


def _filter_eligible_students(df_student: pd.DataFrame) -> pd.DataFrame:
    return df_student.loc[
        df_student["status"].eq("Active")
        & df_student["ketersediaan"].eq("Available")
        & df_student["CV"].eq("Ada")
        & df_student["eligible"].eq("Ya")
    ].copy()


def _load_source_tables(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_request = pd.read_parquet(data_dir / "df_request.parquet")
    df_student = pd.read_parquet(data_dir / "df_student_profile.parquet")
    request_cols = [
        "id_talent_req",
        "nama_posisi",
        "jenis_penempatan",
        "working_arrangement",
        "deskripsi_requirement",
        "bidang_studi_dibutuhkan_normalized",
        "minimum_semester",
    ]
    existing = [c for c in request_cols if c in df_request.columns]
    return df_request[existing].drop_duplicates("id_talent_req"), df_student


def _encode_texts(
    texts: list[str],
    model: Any,
    show_progress: bool = True,
    prompt_name: str | None = None,
) -> np.ndarray:
    kwargs: dict[str, Any] = dict(
        batch_size=BATCH_SIZE,
        show_progress_bar=show_progress,
        normalize_embeddings=True,
    )
    if prompt_name is not None:
        kwargs["prompt_name"] = prompt_name
    return model.encode(texts, **kwargs)


def build_all(data_dir: str | Path | None = None, top_k: int = TOP_K) -> dict[str, Any]:
    processed = (
        Path(data_dir).expanduser().resolve() if data_dir else _PROCESSED_DIR
    )
    df_request, df_student = _load_source_tables(processed)
    eligible = _filter_eligible_students(df_student)
    print(f"Building request texts for {len(df_request)} requests ...")
    request_texts = df_request.apply(build_request_text, axis=1).tolist()
    print(f"Building student texts for {len(eligible)} eligible students ...")
    student_texts = eligible.apply(build_student_text, axis=1).tolist()
    student_nims = eligible["NIM"].tolist()
    from sentence_transformers import SentenceTransformer

    print(f"Loading model {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
    print("Encoding request vectors ...")
    request_vecs = _encode_texts(request_texts, model, prompt_name="query")
    print(f"Encoding {len(student_texts)} student vectors ...")
    student_vecs = _encode_texts(student_texts, model)
    rows: list[dict[str, Any]] = []
    request_ids = df_request["id_talent_req"].tolist()
    min_semester_map: dict[str, int] = {}
    if "minimum_semester" in df_request.columns:
        min_semester_map = df_request.set_index("id_talent_req")["minimum_semester"].to_dict()
    n_requests = len(request_vecs)
    n_students = len(student_vecs)
    print(f"Computing similarity for {n_requests} requests x {n_students} students ...")
    for batch_start in range(0, n_requests, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, n_requests)
        batch_vecs = request_vecs[batch_start:batch_end]
        similarities = np.dot(batch_vecs, student_vecs.T)
        top_indices = np.argsort(-similarities, axis=1)[:, :top_k]
        for batch_idx in range(len(batch_vecs)):
            req_idx = batch_start + batch_idx
            req_id = request_ids[req_idx]
            for rank, stud_idx in enumerate(top_indices[batch_idx]):
                rows.append(
                    {
                        "id_talent_req": req_id,
                        "NIM": student_nims[stud_idx],
                        "semantic_score": round(float(similarities[batch_idx, stud_idx]), 6),
                        "semantic_rank": int(rank) + 1,
                        "minimum_semester": int(min_semester_map.get(req_id, 0)),
                    }
                )
        if (batch_start // BATCH_SIZE) % 10 == 0:
            print(f"  Processed {batch_end}/{n_requests} requests ...")

    scores = pd.DataFrame(rows)
    output_path = _PROCESSED_DIR / "semantic_scores.parquet"
    scores.to_parquet(output_path, index=False)
    metadata = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_NAME,
        "embedding_dim": int(student_vecs.shape[1]),
        "top_k": top_k,
        "num_requests": n_requests,
        "num_students_eligible": n_students,
        "total_pairs_scored": len(rows),
        "output": str(output_path),
    }
    metadata_path = _PROCESSED_DIR / "semantic_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    return metadata


def evaluate_top_k(
    data_dir: str | Path | None = None,
    top_k: int = 5,
    num_requests: int = 5,
) -> pd.DataFrame:
    """Compare semantic ranking vs keyword baseline for representative requests."""
    processed = (
        Path(data_dir).expanduser().resolve() if data_dir else _PROCESSED_DIR
    )
    df_request, df_student = _load_source_tables(processed)
    eligible = _filter_eligible_students(df_student)
    scores_path = processed / "semantic_scores.parquet"
    if not scores_path.exists():
        raise FileNotFoundError(
            f"Semantic scores not found at {scores_path}. "
            "Run build_all() first to precompute request–student similarity scores."
        )
    sample = df_request.sample(n=min(num_requests, len(df_request)), random_state=42)
    semantic_scores = pd.read_parquet(scores_path)
    rows = []
    for _, request in sample.iterrows():
        req_id = request["id_talent_req"]
        sem = semantic_scores.loc[semantic_scores["id_talent_req"] == req_id].nlargest(top_k, "semantic_score")
        for _, score_row in sem.iterrows():
            student = eligible.loc[eligible["NIM"] == score_row["NIM"]]
            if student.empty:
                continue
            student = student.iloc[0]
            baseline = baseline_keyword_score(request, student)
            rows.append(
                {
                    "id_talent_req": req_id,
                    "NIM": score_row["NIM"],
                    "program_studi": student.get("program_studi", ""),
                    "tools": student.get("tools_normalized", ""),
                    "semantic_score": score_row["semantic_score"],
                    "semantic_rank": score_row["semantic_rank"],
                    "baseline_score": round(baseline, 4),
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    result = build_all()
    print(json.dumps(result, indent=2, ensure_ascii=False))
