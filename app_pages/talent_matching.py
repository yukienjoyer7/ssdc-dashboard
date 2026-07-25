import streamlit as st

from components.charts import chart_surface, render_histogram
from components.carbon_ui import render_feedback
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from config.theme import RECOMMENDATION_COLORS
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
        columns_per_row=3,
        variant="primary",
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
        {
            "label": "Kandidat dievaluasi",
            "value": format_count(len(ranked)),
            "help": f"Untuk permintaan {request_id}",
        },
        {
            "label": "Kandidat memenuhi syarat",
            "value": format_count(eligible_count),
            "help": f"{format_percent(eligibility_rate)} dari kandidat dievaluasi",
        },
        {
            "label": "Tingkat kelayakan",
            "value": format_percent(eligibility_rate),
            "help": f"{format_count(eligible_count)} dari {format_count(len(ranked))} kandidat",
        },
        {
            "label": "Kandidat teratas",
            "value": format_count(len(displayed)),
            "help": f"Skor relevansi ≥ {min_score:.2f}",
        },
    ], columns_per_row=4, variant="primary")

    render_section("Daftar pendek berperingkat", "Skor relevansi semantik (bukan probabilitas penerimaan). Nilai lebih tinggi = lebih relevan.")
    if displayed.empty:
        render_empty("Tidak ada kandidat yang cocok", "Turunkan ambang relevansi atau sertakan kandidat yang perlu ditinjau.")
    else:
        columns = [
            "NIM", "nama", "program_studi", "semester", "ketersediaan", "eligible",
            "semantic_score", "semantic_rank", "recommendation",
            "matched_skills", "caution", "explanation",
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
                    color_map=RECOMMENDATION_COLORS,
                    y_title="Kandidat",
                    show_title=False,
                )
        with right:
            candidate_ids = displayed["NIM"].tolist()
            chosen = st.selectbox("Detail kandidat", candidate_ids, key="matching_candidate_detail")
            detail = displayed.loc[displayed["NIM"] == chosen].iloc[0]
            
            # Header
            eligible = bool(detail.get("eligible", False))
            kelayakan_label = "Memenuhi syarat" if eligible else "Tinjau"
            tag_class = "cds-candidate-detail__tag--success" if eligible else "cds-candidate-detail__tag--warning"
            kelayakan_tag = f'<span class="cds-candidate-detail__tag {tag_class}">{kelayakan_label}</span>'
            
            st.markdown(
                '<div class="cds-candidate-detail__header">'
                f'<p class="cds-candidate-detail__name">{detail["nama"]}</p>'
                f'<p class="cds-candidate-detail__program">{detail["program_studi"]} · {kelayakan_label}</p>'
                '</div>',
                unsafe_allow_html=True,
            )
            
            # Explanation
            explanation = detail.get("explanation", "")
            if explanation:
                st.markdown(
                    f'<div class="cds-candidate-detail__explanation">{explanation}</div>',
                    unsafe_allow_html=True,
                )
            
            # KPI metrics
            render_kpis([
                {"label": "Skor relevansi", "value": f"{float(detail['semantic_score']):.3f}"},
                {"label": "Peringkat", "value": str(int(detail["semantic_rank"]))},
                {"label": "Semester", "value": str(detail.get("semester", ""))},
                {"label": "IPK", "value": f"{float(detail.get('IPK', 0)):.2f}" if detail.get("IPK") else "-"},
            ], columns_per_row=4, variant="compact")
            
            # Detail fields
            ketersediaan = str(detail.get("ketersediaan", ""))
            ketersedia_label = "Tersedia" if ketersediaan == "Available" else ketersediaan
            domisili = str(detail.get("domisili", ""))
            keahlian = str(detail.get("tools_normalized", ""))
            keahlian_cocok = str(detail.get("matched_skills", ""))
            caution = str(detail.get("caution", ""))
            
            fields = []
            fields.append(
                '<div class="cds-candidate-detail__field">'
                '<span class="cds-candidate-detail__label">Kelayakan</span>'
                f'<span>{kelayakan_tag}</span>'
                '</div>'
            )
            fields.append(
                '<div class="cds-candidate-detail__field">'
                '<span class="cds-candidate-detail__label">Ketersediaan</span>'
                f'<span class="cds-candidate-detail__value">{ketersedia_label}</span>'
                '</div>'
            )
            if domisili:
                fields.append(
                    '<div class="cds-candidate-detail__field">'
                    '<span class="cds-candidate-detail__label">Domisili</span>'
                    f'<span class="cds-candidate-detail__value">{domisili}</span>'
                    '</div>'
                )
            if keahlian:
                fields.append(
                    '<div class="cds-candidate-detail__field">'
                    '<span class="cds-candidate-detail__label">Keahlian</span>'
                    f'<span class="cds-candidate-detail__skills">{keahlian}</span>'
                    '</div>'
                )
            if keahlian_cocok:
                fields.append(
                    '<div class="cds-candidate-detail__field">'
                    '<span class="cds-candidate-detail__label">Keahlian cocok</span>'
                    f'<span class="cds-candidate-detail__skills">{keahlian_cocok}</span>'
                    '</div>'
                )
            
            fields_html = '<div class="cds-candidate-detail__fields">' + "".join(fields) + '</div>'
            st.markdown(fields_html, unsafe_allow_html=True)
            
            # Caution
            if caution:
                st.markdown(
                    f'<div class="cds-candidate-detail__caution">{caution}</div>',
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
