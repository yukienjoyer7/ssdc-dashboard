from data.loaders import load_dashboard_data


def test_missing_data_directory_uses_anonymized_fallback(tmp_path) -> None:
    result = load_dashboard_data(str(tmp_path / "missing"))

    assert result.is_mock is True
    assert result.source == "Built-in anonymized preview"
    assert "talent_request.csv" in result.tables
    assert result.warnings
