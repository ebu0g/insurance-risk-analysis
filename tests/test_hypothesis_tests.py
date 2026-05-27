"""Unit tests for hypothesis testing helpers."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hypothesis_tests import (compare_binary_kpi,  # noqa: E402
                              compare_numeric_kpi, prepare_analysis_frame,
                              run_task3_analysis)


@pytest.fixture
def sample_data():
    """Create a small insurance sample for hypothesis tests."""
    return pd.DataFrame(
        {
            "PolicyID": [
                "P001",
                "P002",
                "P003",
                "P004",
                "P005",
                "P006",
                "P007",
                "P008",
                "P009",
            ],
            "Province": [
                "Gauteng",
                "Western Cape",
                "KZN",
                "Gauteng",
                "Western Cape",
                "KZN",
                "Gauteng",
                "Western Cape",
                "Gauteng",
            ],
            "Gender": ["M", "F", "M", "F", "M", "M", "F", "F", "M"],
            "ZipCode": [
                "2000",
                "8000",
                "4001",
                "2001",
                "8001",
                "4002",
                "2002",
                "8002",
                "2003",
            ],
            "TotalPremium": [5200, 4300, 6100, 3900, 4700, 7200, 3600, 5100, 5800],
            "TotalClaims": [1800, 0, 2500, 0, 900, 5200, 0, 1200, 3100],
        }
    )


def test_prepare_analysis_frame_adds_expected_columns(sample_data):
    """The analysis frame should contain reusable KPI columns."""
    analysis_df = prepare_analysis_frame(sample_data)

    assert "HasClaim" in analysis_df.columns
    assert "Margin" in analysis_df.columns
    assert "ClaimSeverity" in analysis_df.columns
    assert analysis_df.loc[0, "HasClaim"] == 1
    assert analysis_df.loc[1, "HasClaim"] == 0
    assert analysis_df.loc[0, "Margin"] == 3400


def test_compare_binary_kpi_returns_decision(sample_data):
    """Binary KPI comparisons should produce a valid hypothesis result."""
    result = compare_binary_kpi(
        sample_data,
        feature="Gender",
        group_a="F",
        group_b="M",
        kpi="HasClaim",
        hypothesis="H0: No risk difference between women and men",
    )

    assert result["test"] == "Chi-squared test"
    assert 0 <= result["p_value"] <= 1
    assert result["decision"] in {"Reject H0", "Fail to reject H0"}
    assert result["group_a"] == "F"
    assert result["group_b"] == "M"


def test_compare_numeric_kpi_returns_decision(sample_data):
    """Numeric KPI comparisons should produce a valid hypothesis result."""
    result = compare_numeric_kpi(
        sample_data,
        feature="Province",
        group_a="Gauteng",
        group_b="Western Cape",
        kpi="Margin",
        hypothesis="H0: No margin difference across provinces",
    )

    assert result["test"] == "Welch t-test"
    assert 0 <= result["p_value"] <= 1
    assert result["decision"] in {"Reject H0", "Fail to reject H0"}
    assert result["group_a_n"] > 0
    assert result["group_b_n"] > 0


def test_run_task3_analysis_builds_results_table(sample_data):
    """The task runner should produce the four Task 3 results."""
    results = run_task3_analysis(sample_data)

    assert len(results) == 4
    assert set(results["hypothesis"]) == {
        "H0: No risk differences across provinces",
        "H0: No risk differences between zip codes",
        "H0: No significant margin difference between zip codes",
        "H0: No risk difference between Women and Men",
    }
    assert set(results["decision"]).issubset({"Reject H0", "Fail to reject H0"})
