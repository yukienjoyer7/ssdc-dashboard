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
        "03 / Candidate shortlist",
        "Talent Matching",
        "Which eligible students are the strongest matches for a selected talent request, and why?",
        provisional_note=(
            "Eligibility requires a study-program/interest match, minimum semester, "
            "and Available status."
        ),
    )
    requests = request_table(data, filters)
    if requests.empty:
        render_empty("No requests available", "Adjust the global filters before selecting a request.")
        return
    options = requests["id_talent_req"].tolist()
    previous = st.session_state.get("selected_request_id")
    default_index = options.index(previous) if previous in options else 0
    request_id = st.selectbox("Select talent request", options, index=default_index, key="matching_request_id")
    st.session_state["selected_request_id"] = request_id
    ranked, request = matching_table(data, request_id, filters)
    if request is None:
        render_empty("Request not found", "Choose a request from the current filtered list.")
        return

    render_kpis(
        [
            {"label": "Company", "value": str(request["company_name"])},
            {"label": "Position", "value": str(request["nama_posisi"])},
            {"label": "Requested headcount", "value": format_count(request["requested_headcount"])},
        ],
        key="matching-request-context",
    )
    render_feedback(
        "Request requirements",
        f"Study program: {request['bidang_studi_dibutuhkan']} · "
        f"Minimum semester: {request['minimum_semester']} · "
        f"Placement: {request['jenis_penempatan']}",
        key="matching-request-requirements",
    )

    with control_group("Refine shortlist", key="matching-filters"):
        eligibility_only = st.checkbox("Show eligible candidates only", value=True, key="matching_eligible_only")
        min_score = st.slider("Minimum match score", 0, 100, 0, key="matching_min_score")
    displayed = ranked.loc[ranked["match_score"] >= min_score].copy()
    if eligibility_only:
        displayed = displayed.loc[displayed["eligible"]].copy()
    eligible_count = int(ranked["eligible"].sum())
    eligibility_rate = eligible_count / len(ranked) * 100 if len(ranked) else 0
    render_kpis([
        {"label": "Evaluated candidates", "value": format_count(len(ranked))},
        {"label": "Eligible candidates", "value": format_count(eligible_count)},
        {"label": "Eligibility rate", "value": format_percent(eligibility_rate)},
        {"label": "Top-k candidates", "value": format_count(len(displayed))},
    ], columns_per_row=4, variant="compact")

    render_section("Ranked shortlist", "Every score includes criterion-level explanation for review.")
    if displayed.empty:
        render_empty("No candidates match", "Lower the score threshold or include candidates who need review.")
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
                "Candidates by match score",
                "Exact score values grouped by recommendation outcome.",
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
                    "Candidates by match score",
                    color="recommendation",
                    show_title=False,
                    color_map=RECOMMENDATION_COLORS,
                    x_title="Match score",
                    y_title="Candidates",
                    category_order=score_counts["score_label"].drop_duplicates().tolist(),
                    tick_angle=0,
                )
        with right:
            candidate_ids = displayed["NIM"].tolist()
            chosen = st.selectbox("Candidate detail", candidate_ids, key="matching_candidate_detail")
            detail = displayed.loc[displayed["NIM"] == chosen].iloc[0]
            st.markdown(f"**{detail['nama']}** · {detail['program_studi']}")
            st.write(detail["explanation"])
            st.write({
                "Eligibility": "Eligible" if detail["eligible"] else "Review",
                "Match score": int(detail["match_score"]),
                "Semester": detail["semester"],
                "Availability": detail["ketersediaan"],
            })


if __name__ == "__main__":
    main()
