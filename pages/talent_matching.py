import streamlit as st

from components.charts import render_histogram
from components.states import render_empty, render_provisional_note
from components.tables import render_downloadable_table
from components.ui import format_count, format_percent, render_kpis, render_section
from pages.common import start_page
from services.analytics import matching_table, request_table


def main() -> None:
    data, filters = start_page(
        "03 / Candidate shortlist",
        "Talent Matching",
        "Which eligible students are the strongest matches for a selected talent request, and why?",
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

    left, middle, right = st.columns(3)
    with left:
        st.metric("Company", request["company_name"])
    with middle:
        st.metric("Position", request["nama_posisi"])
    with right:
        st.metric("Requested headcount", int(request["requested_headcount"]))
    st.info(
        f"Requirements: {request['bidang_studi_dibutuhkan']} | "
        f"Minimum semester: {request['minimum_semester']} | "
        f"Placement: {request['jenis_penempatan']}",
        icon=":material/description:",
    )
    render_provisional_note("Eligibility requires a study-program/interest match, minimum semester, and Available status.")

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
    ])

    render_section("Ranked shortlist", "Every score includes criterion-level explanation for review.")
    if displayed.empty:
        render_empty("No candidates match", "Lower the score threshold or include candidates who need review.")
    else:
        columns = [
            "NIM", "nama", "program_studi", "semester", "ketersediaan", "eligible", "match_score",
            "recommendation", "explanation",
        ]
        render_downloadable_table(displayed[columns], "ssdc-ranked-shortlist.csv", "matching-table")
        left, right = st.columns([1, 2])
        with left:
            render_histogram(ranked, "match_score", "Match-score distribution", color="recommendation")
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
