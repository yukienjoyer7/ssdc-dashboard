import pandas as pd
import streamlit as st

from components.carbon_ui import render_table


COLUMN_LABELS_ID = {
    "id_talent_req": "ID permintaan",
    "id_tracking_student": "ID pelacakan",
    "company_name": "Perusahaan",
    "nama_posisi": "Posisi",
    "position": "Posisi",
    "requested_headcount": "Kebutuhan talenta",
    "placements": "Penempatan",
    "headcount_gap": "Kesenjangan kebutuhan",
    "request_aging_days": "Usia permintaan (hari)",
    "action_label": "Label tindakan",
    "request_status": "Status permintaan",
    "candidate_applications": "Lamaran kandidat",
    "NIM": "NIM",
    "student_name": "Nama kandidat",
    "nama": "Nama kandidat",
    "program_studi": "Program studi",
    "study_program": "Program studi",
    "semester": "Semester",
    "ketersediaan": "Ketersediaan",
    "eligible": "Memenuhi syarat",
    "match_score": "Skor kecocokan",
    "semantic_score": "Skor relevansi",
    "semantic_rank": "Peringkat relevansi",
    "recommendation": "Rekomendasi",
    "matched_skills": "Keahlian cocok",
    "caution": "Perhatian",
    "explanation": "Penjelasan",
    "progress_student": "Tahap seleksi",
    "canonical_outcome": "Hasil kanonis",
    "last_update": "Pembaruan terakhir",
    "selection_aging_days": "Usia seleksi (hari)",
    "stale_flag": "Penanda kedaluwarsa",
    "ghosting_warning": "Peringatan ghosting",
    "placement_type": "Jenis penempatan",
    "placement_date": "Tanggal penempatan",
    "time_to_placement_days": "Waktu hingga penempatan (hari)",
}

DISPLAY_VALUES_ID = {
    "Submitted": "Dikirim",
    "Interview User": "Wawancara pengguna",
    "FU 1": "TL 1",
    "FU 2": "TL 2",
    "FU 3": "TL 3",
    "Finish": "Selesai",
    "Placement": "Penempatan",
    "Ghosting": "Ghosting",
    "Rejected": "Ditolak",
    "On Progress": "Dalam proses",
    "Closed": "Ditutup",
    "Available": "Tersedia",
    "Unavailable": "Tidak tersedia",
    "Untracked": "Tidak terlacak",
    "Strong match": "Kecocokan kuat",
    "Potential match": "Kandidat potensial",
    "Review": "Tinjau",
    "Eligible": "Memenuhi syarat",
    "Active": "Aktif",
    "Available": "Tersedia",
    "true": "Ya",
    "false": "Tidak",
}


def render_downloadable_table(frame: pd.DataFrame, filename: str, key: str, height: int = 420) -> None:
    columns = [(column, COLUMN_LABELS_ID.get(column, column.replace("_", " ").title())) for column in frame.columns]
    render_table(frame, columns=columns, key=f"{key}-carbon")
    if frame.empty:
        return
    st.download_button(
        "Unduh CSV terfilter",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
        icon=":material/download:",
    )
