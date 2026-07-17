from datetime import date, timedelta

import pandas as pd


def _rows(start: date, count: int) -> list[date]:
    return [start + timedelta(days=index * 9) for index in range(count)]


def build_mock_tables() -> dict[str, pd.DataFrame]:
    dates = _rows(date(2026, 1, 8), 6)
    companies = [
        {"id_company": "C001", "company_name": "Northstar Labs", "company_type": "Startup", "industry_sector": "Technology", "kota": "Surakarta", "skala_perusahaan": "Nasional", "pic_name": "Contact A", "pic_phone": "0000000000", "created_at": "2025-12-01"},
        {"id_company": "C002", "company_name": "Civic Works", "company_type": "Private", "industry_sector": "Consulting", "kota": "Semarang", "skala_perusahaan": "Regional", "pic_name": "Contact B", "pic_phone": "0000000000", "created_at": "2025-12-03"},
        {"id_company": "C003", "company_name": "Meridian Goods", "company_type": "Private", "industry_sector": "Manufacturing", "kota": "Yogyakarta", "skala_perusahaan": "Nasional", "pic_name": "Contact C", "pic_phone": "0000000000", "created_at": "2025-12-07"},
    ]
    requests = []
    tracking = []
    for index, (company, request_date) in enumerate(zip(companies * 2, dates), start=1):
        request_id = f"TR{index:03d}"
        track_id = f"TC{index:03d}"
        headcount = 2 + index % 4
        progress = ["Submitted", "On Review", "Shortlisted", "Closed", "Draft", "Submitted"][index - 1]
        requests.append({
            "id_talent_req": request_id, "id_company": company["id_company"], "nama_perusahaan": company["company_name"],
            "alamat_kantor": "Prototype address", "industri_sektor": company["industry_sector"], "nama_pic": company["pic_name"],
            "no_whatsapp": "0000000000", "nama_posisi": ["Data Analyst", "Project Coordinator", "Operations Intern"][index % 3],
            "jenis_penempatan": ["Magang", "Part-time", "Full-time"][index % 3], "headcount": str(headcount),
            "bidang_studi_dibutuhkan": ["Statistika, Manajemen", "Teknik Industri, Manajemen", "Informatika"][index % 3],
            "minimum_semester": str(3 + index % 4), "deskripsi_requirement": "Prototype requirement",
            "working_arrangement": "Hybrid", "working_arrangement_detail": "Prototype arrangement", "durasi": "3 Bulan",
            "renumerasi": "Rp 1.000.000/bulan", "request_date": request_date.isoformat(), "sumber_baris_form": "Prototype",
            "renumerasi_category": "Paid", "durasi_months": str(3),
            "bidang_studi_dibutuhkan_normalized": ["Manajemen, Statistika", "Manajemen, Teknik Industri", "Informatika"][index % 3],
        })
        sent = max(0, headcount - index % 3)
        tracking.append({
            "id_tracking_company": track_id, "id_talent_req": request_id, "id_company": company["id_company"],
            "nama_perusahaan": company["company_name"], "posisi": requests[-1]["nama_posisi"], "jenis_penempatan": requests[-1]["jenis_penempatan"],
            "bidang_studi_dicari": requests[-1]["bidang_studi_dibutuhkan"], "progress": progress,
            "request_date": request_date.isoformat(), "send_date": (request_date + timedelta(days=12)).isoformat(),
            "jumlah_permintaan": str(headcount), "jumlah_dikirimkan": str(sent),
            "list_nim": ", ".join(f"2026000{index}{n}" for n in range(sent)),
            "bidang_studi_dicari_normalized": ["Manajemen, Statistika", "Manajemen, Teknik Industri", "Informatika"][index % 3],
        })

    candidates = []
    statuses = []
    for index in range(1, 13):
        nim = f"202600{index:03d}"
        program = ["Statistika", "Manajemen", "Teknik Industri", "Informatika"][index % 4]
        candidates.append({
            "NIM": nim, "nama": f"Candidate {index:02d}", "program_studi": program, "semester": str(2 + index % 6),
            "hp": "0000000000", "email_pribadi": f"candidate{index}@example.invalid", "email_kampus": f"candidate{index}@campus.invalid",
            "bidang_minat": program, "jenis_penempatan_diminati": "Magang", "bulan_masuk": "2026-01",
            "bulan_masuk_month": "01", "bulan_masuk_year": "2026",
        })
        statuses.append({
            "id_status": f"SS{index:04d}", "NIM": nim, "email": f"candidate{index}@campus.invalid", "nama": f"Candidate {index:02d}",
            "semester": str(2 + index % 6), "program_studi": program, "no_whatsapp": "0000000000", "CV": "Ada",
            "portofolio": "Ada", "IPK": f"{3.0 + (index % 10) / 10:.2f}", "status": "Active", "domisili": "Surakarta",
            "ketersediaan": "Available", "tools": "Excel, Python", "sync_date": "2026-01-10",
            "placement_verified": "Tidak", "eligible": "Ya", "tools_normalized": "Excel, Python",
        })

    selection = []
    stages = ["Submitted", "Interview User", "Ghosting", "Placement", "Finish", "FU 1"]
    for index in range(1, 19):
        request_index = (index - 1) % 6
        candidate_index = (index - 1) % 12
        selection.append({
            "id_tracking_student": f"TS{index:04d}", "NIM": candidates[candidate_index]["NIM"],
            "id_tracking_company": tracking[request_index]["id_tracking_company"], "student_name": candidates[candidate_index]["nama"],
            "internship_semester": candidates[candidate_index]["semester"], "company": tracking[request_index]["nama_perusahaan"],
            "position": tracking[request_index]["posisi"], "jenis_penempatan": tracking[request_index]["jenis_penempatan"],
            "progress_student": stages[(index - 1) % len(stages)], "last_update": (dates[request_index] + timedelta(days=18 + index)).isoformat(),
            "rejection": "",
        })

    return {
        "company.csv": pd.DataFrame(companies),
        "status_student.csv": pd.DataFrame(statuses),
        "student_all.csv": pd.DataFrame(candidates),
        "talent_request.csv": pd.DataFrame(requests),
        "tracking_company.csv": pd.DataFrame(tracking),
        "tracking_student.csv": pd.DataFrame(selection),
    }
