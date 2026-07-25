import streamlit as st

from components.charts import chart_surface, render_bar
from components.carbon_ui import render_feedback
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from config.theme import RECOMMENDATION_COLORS
from services.analytics import matching_table, request_table


def main() -> None:
    data, filters = start_page(
        "03 / Daftar pendek kandidat",
        "Pencocokan Talenta",
        "Kandidat yang memenuhi syarat mana yang paling sesuai untuk permintaan talenta terpilih, dan mengapa?",
        provisional_note=(
            "Kelayakan memerlukan kecocokan program studi/minat, semester minimum, "
            "dan status Tersedia."
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
    ranked, request = matching_table(data, request_id, filters)
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

    with control_group("Saring daftar pendek", key="matching-filters"):
        eligibility_only = st.checkbox("Tampilkan hanya kandidat yang memenuhi syarat", value=True, key="matching_eligible_only")
        min_score = st.slider("Skor kecocokan minimum", 0, 100, 0, key="matching_min_score")
    displayed = ranked.loc[ranked["match_score"] >= min_score].copy()
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

    render_section("Daftar pendek berperingkat", "Setiap skor dilengkapi penjelasan per kriteria untuk ditinjau.")
    if displayed.empty:
        render_empty("Tidak ada kandidat yang cocok", "Turunkan ambang skor atau sertakan kandidat yang perlu ditinjau.")
    else:
        columns = [
            "NIM", "nama", "program_studi", "semester", "ketersediaan", "eligible", "match_score",
            "recommendation", "explanation",
        ]
        render_downloadable_table(displayed[columns], "ssdc-ranked-shortlist.csv", "matching-table")
        left, right = analytical_columns(
            "supporting_main",
            key="matching-candidate-detail",
        )
        with left:
            with chart_surface(
                "Kandidat berdasarkan skor kecocokan",
                "Nilai skor tepat dikelompokkan berdasarkan hasil rekomendasi.",
                key="matching-score-distribution",
            ):
                score_counts = (
                    ranked.groupby(["match_score", "recommendation"], as_index=False)
                    .size()
                    .rename(columns={"size": "candidates"})
                    .sort_values("match_score")
                )
                score_counts["score_label"] = score_counts["match_score"].astype(int).astype(str)
                render_bar(
                    score_counts,
                    "score_label",
                    "candidates",
                    "Kandidat berdasarkan skor kecocokan",
                    color="recommendation",
                    show_title=False,
                    color_map=RECOMMENDATION_COLORS,
                    x_title="Skor kecocokan",
                    y_title="Kandidat",
                    category_order=score_counts["score_label"].drop_duplicates().tolist(),
                    tick_angle=0,
                )
        with right:
            candidate_ids = displayed["NIM"].tolist()
            chosen = st.selectbox("Detail kandidat", candidate_ids, key="matching_candidate_detail")
            detail = displayed.loc[displayed["NIM"] == chosen].iloc[0]
            st.markdown(f"**{detail['nama']}** · {detail['program_studi']}")
            st.write(detail["explanation"])
            st.write({
                "Kelayakan": "Memenuhi syarat" if detail["eligible"] else "Tinjau",
                "Skor kecocokan": int(detail["match_score"]),
                "Semester": detail["semester"],
                "Ketersediaan": detail["ketersediaan"],
            })


if __name__ == "__main__":
    main()
