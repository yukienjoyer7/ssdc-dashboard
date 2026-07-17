from data.contracts import EXPECTED_COLUMNS, TABLE_FILES
from data.loaders import load_dashboard_data
from data.mock_data import build_mock_tables


def test_missing_data_directory_uses_anonymized_fallback(tmp_path) -> None:
    result = load_dashboard_data(str(tmp_path / "missing"))

    assert result.is_mock is True
    assert result.source == "Built-in anonymized preview"
    assert "talent_request.csv" in result.tables
    assert result.warnings


def test_mock_tables_match_expected_columns() -> None:
    tables = build_mock_tables()
    for filename in TABLE_FILES:
        actual = set(tables[filename].columns)
        expected = set(EXPECTED_COLUMNS[filename])
        missing = sorted(expected - actual)
        assert not missing, f"{filename} missing expected columns: {missing}"
