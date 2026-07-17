from dataclasses import dataclass
from datetime import date
from pathlib import Path


TABLE_FILES = (
    "company.csv",
    "status_student.csv",
    "student_all.csv",
    "talent_request.csv",
    "tracking_company.csv",
    "tracking_student.csv",
)

EXPECTED_COLUMNS = {
    "company.csv": [
        "id_company", "company_name", "company_type", "industry_sector", "kota",
        "skala_perusahaan", "pic_name", "pic_phone", "created_at",
    ],
    "status_student.csv": [
        "id_status", "NIM", "email", "nama", "semester", "program_studi",
        "no_whatsapp", "CV", "portofolio", "IPK", "status", "domisili",
        "ketersediaan", "tools", "sync_date", "placement_verified",
        "eligible", "tools_normalized",
    ],
    "student_all.csv": [
        "NIM", "nama", "program_studi", "semester", "hp", "email_pribadi",
        "email_kampus", "bidang_minat", "jenis_penempatan_diminati", "bulan_masuk",
        "bulan_masuk_month", "bulan_masuk_year",
    ],
    "talent_request.csv": [
        "id_talent_req", "id_company", "nama_perusahaan", "alamat_kantor",
        "industri_sektor", "nama_pic", "no_whatsapp", "nama_posisi", "jenis_penempatan",
        "headcount", "bidang_studi_dibutuhkan", "minimum_semester",
        "deskripsi_requirement", "working_arrangement", "working_arrangement_detail",
        "durasi", "renumerasi", "request_date", "sumber_baris_form",
        "renumerasi_category", "durasi_months",
        "bidang_studi_dibutuhkan_normalized",
    ],
    "tracking_company.csv": [
        "id_tracking_company", "id_talent_req", "id_company", "nama_perusahaan", "posisi",
        "jenis_penempatan", "bidang_studi_dicari", "progress", "request_date", "send_date",
        "jumlah_permintaan", "jumlah_dikirimkan", "list_nim",
        "bidang_studi_dicari_normalized",
    ],
    "tracking_student.csv": [
        "id_tracking_student", "NIM", "id_tracking_company", "student_name", "internship_semester",
        "company", "position", "jenis_penempatan", "progress_student", "last_update", "rejection",
    ],
}


@dataclass(frozen=True)
class FilterState:
    date_start: date | None = None
    date_end: date | None = None
    company: str = "All companies"
    study_program: str = "All study programs"
    request_status: str = "All request statuses"
    placement_type: str = "All placement types"


def missing_columns(table_name: str, columns: list[str]) -> list[str]:
    expected = set(EXPECTED_COLUMNS[table_name])
    return sorted(expected.difference(columns))
