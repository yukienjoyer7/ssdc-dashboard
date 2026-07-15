# Dashboard Data Contract

## Source

The dashboard reads six UTF-8 CSVs from `SSDC_DATA_DIR`. When unset, the
default is the sibling path:

```text
../ssdc-data-cleaning/data_clean
```

The loader validates the expected columns before enabling local-data mode. A
missing directory or incomplete contract uses the built-in anonymized preview
so the public repository still launches without personal data.

## Dashboard-facing entities

- `talent_request.csv`: request identity, company, role, headcount, requirements, and request date.
- `tracking_company.csv`: request progress, candidates sent, and request-level placement linkage.
- `student_all.csv`: candidate profile and study interests.
- `status_student.csv`: candidate status, study program, semester, and availability.
- `tracking_student.csv`: candidate-selection record, current stage, and last update.
- `company.csv`: company labels and dimensions.

Pages depend on `services/analytics.py`, not on raw file paths. This keeps page
code stable when the Data Engineer changes the upstream export location.

## Sensitive data

CSV files are ignored by Git and are never included in the public repository.
Use an environment variable or a local sibling checkout to provide them.
