"""Unit tests for data loading module"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loader import InsuranceDataLoader


@pytest.fixture
def sample_data():
    """Create sample insurance data for testing."""
    data = {
        "PolicyID": ["P001", "P002", "P003"],
        "TotalPremium": [5000, 3500, 7200],
        "TotalClaims": [2000, 0, 5500],
        "Province": ["Gauteng", "Western Cape", "Gauteng"],
        "VehicleType": ["Sedan", "SUV", "Sedan"],
        "Gender": ["M", "F", "M"],
        "ZipCode": ["2000", "8000", "2050"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_data_file(tmp_path, sample_data):
    """Save sample data to temporary CSV file."""
    filepath = tmp_path / "test_data.csv"
    sample_data.to_csv(filepath, index=False)
    return str(filepath)


def test_data_loader_initialization():
    """Test InsuranceDataLoader initialization."""
    loader = InsuranceDataLoader("test.csv")
    assert loader.data_path == Path("test.csv")
    assert loader.df is None


def test_load_data(temp_data_file):
    """Test loading data from CSV."""
    loader = InsuranceDataLoader(temp_data_file)
    df = loader.load()
    assert df is not None
    assert len(df) == 3
    assert "PolicyID" in df.columns


def test_check_missing_values(sample_data):
    """Test missing value detection."""
    loader = InsuranceDataLoader("dummy.csv")
    loader.df = sample_data
    missing = loader.check_missing_values()
    assert len(missing) == 0  # No missing values in sample


def test_handle_missing_values(sample_data):
    """Test missing value handling."""
    sample_data.loc[0, "TotalClaims"] = np.nan
    loader = InsuranceDataLoader("dummy.csv")
    loader.df = sample_data

    df_clean = loader.handle_missing_values(strategy="drop")
    assert len(df_clean) == 2  # One row dropped


def test_create_derived_features(sample_data):
    """Test feature engineering."""
    loader = InsuranceDataLoader("dummy.csv")
    df_feat = loader.create_derived_features(sample_data)

    assert "LossRatio" in df_feat.columns
    assert "Margin" in df_feat.columns
    assert "HasClaim" in df_feat.columns

    # Check calculations
    assert df_feat.loc[0, "LossRatio"] == pytest.approx(2000 / 5000)
    assert df_feat.loc[0, "Margin"] == 5000 - 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
