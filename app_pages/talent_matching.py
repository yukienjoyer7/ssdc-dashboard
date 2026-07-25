import streamlit as st

from components.charts import chart_surface, render_histogram
from components.carbon_ui import render_feedback
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from services.analytics import request_table, semantic_matching_table


def main() -> None:
    data, filters = start_page(
        "03 / Daftar pendek kandidat",
        "Pencocokan Talenta",
        "Kandidat yang memenuhi syarat mana yang paling sesuai untuk permintaan talenta terpilih, dan mengapa?",
        provisional_note=(
            "Peringkat semantik menggunakan Qwen3-Embedding-0.6B. Gerbang kelayakan: "
            "status Aktif, Tersedia, CV, dan semester minimum per permintaan."
        ),
    )
    requests = request_table(data, filters)
    if requests.empty:
        render_empty("Tidak ada permintaan tersedia", "Sesuaikan filter global sebelum memilih permintaan.")
        return
    options = requests["id_talent_req"].tolist()
    previous = st.session_state.get("selected_request_id")
    default_index = options.index(previous) if previous in options else 0
    request_id = st.selectbox("Pilih permintaan talenta", options, index=default_index, key="matching_request_id")
    st.session_state["selected_request_id"] = request_id
    ranked, request = semantic_matching_table(data, request_id, filters)
    if request is None:
        render_empty("Permintaan tidak ditemukan", "Pilih permintaan dari daftar terfilter saat ini.")
        return

    render_kpis(
        [
            {"label": "Perusahaan", "value": str(request["company_name"])},
            {"label": "Posisi", "value": str(request["nama_posisi"])},
            {"label": "Kebutuhan talenta", "value": format_count(request["requested_headcount"])},
        ],
        key="matching-request-context",
    )
    render_feedback(
        "Persyaratan permintaan",
        f"Program studi: {request['bidang_studi_dibutuhkan']} · "
        f"Semester minimum: {request['minimum_semester']} · "
        f"Penempatan: {request['jenis_penempatan']}",
        key="matching-request-requirements",
    )

    if ranked.attrs.get("score_source") == "rule_based_fallback":
        render_feedback(
            "Pencocokan sementara",
            "Skor semantik belum tersedia; hasil berikut menggunakan pencocokan berbasis aturan.",
            kind="warning",
            key="matching-semantic-fallback",
        )

    if ranked.empty:
        render_empty(
            "Skor semantik tidak tersedia",
            "Skor semantik terpraproses tidak ditemukan. Jalankan pipeline pencocokan semantik "
            "(services/semantic_matching.py build_all()) untuk membuat peringkat kandidat.",
        )
        return

    with control_group("Saring daftar pendek", key="matching-filters"):
        eligibility_only = st.checkbox("Tampilkan hanya kandidat yang memenuhi syarat", value=True, key="matching_eligible_only")
        min_score = st.slider("Skor relevansi minimum", 0.00, 1.00, 0.00, 0.05, key="matching_min_score")
    displayed = ranked.loc[ranked["semantic_score"] >= min_score].copy()
    if eligibility_only:
        displayed = displayed.loc[displayed["eligible"]].copy()
    eligible_count = int(ranked["eligible"].sum())
    eligibility_rate = eligible_count / len(ranked) * 100 if len(ranked) else 0
    render_kpis([
        {"label": "Kandidat dievaluasi", "value": format_count(len(ranked))},
        {"label": "Kandidat memenuhi syarat", "value": format_count(eligible_count)},
        {"label": "Tingkat kelayakan", "value": format_percent(eligibility_rate)},
        {"label": "Kandidat teratas", "value": format_count(len(displayed))},
    ], columns_per_row=4, variant="compact")

    render_section("Daftar pendek berperingkat", "Skor relevansi semantik (bukan probabilitas penerimaan). Nilai lebih tinggi = lebih relevan.")
    if displayed.empty:
        render_empty("Tidak ada kandidat yang cocok", "Turunkan ambang relevansi atau sertakan kandidat yang perlu ditinjau.")
    else:
        columns = [
            "NIM", "nama", "program_studi", "semester", "ketersediaan", "eligible",
            "semantic_score", "semantic_rank", "recommendation", "explanation",
        ]
        render_downloadable_table(displayed[columns], "ssdc-ranked-shortlist.csv", "matching-table")
        left, right = analytical_columns(
            "supporting_main",
            key="matching-candidate-detail",
        )
        with left:
            with chart_surface(
                "Distribusi skor relevansi",
                "Skor semantik dikelompokkan berdasarkan hasil rekomendasi.",
                key="matching-score-distribution",
            ):
                render_histogram(
                    ranked,
                    "semantic_score",
                    "Distribusi skor relevansi",
                    color="recommendation",
                    y_title="Kandidat",
                    show_title=False,
                )
        with right:
            candidate_ids = displayed["NIM"].tolist()
            chosen = st.selectbox("Detail kandidat", candidate_ids, key="matching_candidate_detail")
            detail = displayed.loc[displayed["NIM"] == chosen].iloc[0]
            st.markdown(f"**{detail['nama']}** · {detail['program_studi']}")
            st.write(detail["explanation"])
            st.write({
                "Kelayakan": "Memenuhi syarat" if detail["eligible"] else "Tinjau",
                "Skor relevansi": f"{float(detail['semantic_score']):.3f}",
                "Peringkat": int(detail["semantic_rank"]),
                "Semester": str(detail["semester"]),
                "IPK": str(detail.get("IPK", "")),
                "Ketersediaan": "Tersedia" if detail["ketersediaan"] == "Available" else detail["ketersediaan"],
                "Domisili": detail.get("domisili", ""),
                "Keahlian": detail.get("tools_normalized", ""),
            })


if __name__ == "__main__":
    main()
