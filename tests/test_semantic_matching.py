import pandas as pd

from services.semantic_matching import (
    _safe,
    _tokenize_keywords,
    baseline_keyword_score,
    build_request_text,
    build_student_text,
)


def test_safe_returns_default_for_nan() -> None:
    assert _safe(float("nan"), "fallback") == "fallback"
    assert _safe(None, "fallback") == "fallback"
    assert _safe("", "fallback") == "fallback"
    assert _safe("nan", "Tidak tersedia") == "Tidak tersedia"


def test_safe_returns_trimmed_value() -> None:
    assert _safe("  SQL  ") == "SQL"
    assert _safe("Python") == "Python"


def test_request_text_includes_position_and_requirement() -> None:
    row = pd.Series(
        {
            "nama_posisi": "Data Analyst",
            "bidang_studi_dibutuhkan_normalized": "Statistika, Informatika",
            "jenis_penempatan": "Magang",
            "working_arrangement": "Hybrid",
            "deskripsi_requirement": "Menguasai SQL dan Python.",
        }
    )
    text = build_request_text(row)
    assert "Data Analyst" in text
    assert "Statistika" in text
    assert "Magang" in text
    assert "Hybrid" in text
    assert "SQL" in text


def test_request_text_handles_missing_fields() -> None:
    row = pd.Series({})
    text = build_request_text(row)
    assert "Tidak tersedia" in text


def test_student_text_includes_program_and_tools() -> None:
    row = pd.Series(
        {
            "program_studi": "Informatika",
            "bidang_minat": "Data Science",
            "tools_normalized": "Python, SQL, Tableau",
            "jenis_penempatan_diminati": "Full-time",
        }
    )
    text = build_student_text(row)
    assert "Informatika" in text
    assert "Data Science" in text
    assert "Python" in text
    assert "Tableau" in text
    assert "Full-time" in text


def test_tokenize_splits_commas_and_slashes() -> None:
    tokens = _tokenize_keywords("HTML/CSS, JavaScript, React")
    assert "html" in tokens
    assert "css" in tokens
    assert "javascript" in tokens
    assert "react" in tokens


def test_tokenize_filters_stop_words() -> None:
    tokens = _tokenize_keywords("Menguasai, dasar, dalam, baik, dan, serta")
    assert "menguasai" not in tokens
    assert "dasar" not in tokens
    assert "dalam" not in tokens


def test_baseline_keyword_score_identical_tools() -> None:
    request = pd.Series({"bidang_studi_dibutuhkan_normalized": "", "deskripsi_requirement": "Menguasai Python, SQL"})
    student = pd.Series({"tools_normalized": "Python, SQL, Tableau"})
    assert baseline_keyword_score(request, student) > 0


def test_baseline_keyword_score_no_overlap() -> None:
    request = pd.Series({"bidang_studi_dibutuhkan_normalized": "", "deskripsi_requirement": "Komunikasi baik"})
    student = pd.Series({"tools_normalized": "AutoCAD, SolidWorks"})
    assert baseline_keyword_score(request, student) == 0.0


def test_baseline_uses_bidang_studi_field() -> None:
    request = pd.Series({"bidang_studi_dibutuhkan_normalized": "Informatika", "deskripsi_requirement": "Menguasai SQL"})
    student = pd.Series({"tools_normalized": "SQL"})
    assert baseline_keyword_score(request, student) > 0
