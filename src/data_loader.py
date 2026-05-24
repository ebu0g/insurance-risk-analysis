"""Data Loading and Preprocessing Utilities"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsuranceDataLoader:
    """Load and validate ACIS insurance dataset."""
    
    def __init__(self, data_path: str = "data/insurance_data.csv"):
        """
        Initialize data loader.
        
        Args:
            data_path: Path to the insurance CSV file
        """
        self.data_path = Path(data_path)
        self.df = None
        
    def load(self) -> pd.DataFrame:
        """Load insurance data from CSV."""
        try:
            self.df = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(self.df)} records from {self.data_path}")
            return self.df
        except FileNotFoundError:
            logger.error(f"Data file not found: {self.data_path}")
            raise
    
    def validate_dtypes(self) -> Dict[str, str]:
        """
        Validate and report data types.
        
        Returns:
            Dictionary of column names and their dtypes
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load() first.")
        
        dtype_mapping = {
            'PolicyID': 'object',
            'IssueDate': 'datetime64',
            'ExpiryDate': 'datetime64',
            'TotalPremium': 'float64',
            'TotalClaims': 'float64',
            'Province': 'object',
            'VehicleType': 'object',
            'Gender': 'object',
            'ZipCode': 'object',
        }
        
        issues = []
        for col, expected_dtype in dtype_mapping.items():
            if col in self.df.columns:
                actual = str(self.df[col].dtype)
                if expected_dtype not in actual:
                    issues.append(f"{col}: expected {expected_dtype}, got {actual}")
        
        return issues if issues else {"status": "All dtypes valid"}
    
    def check_missing_values(self) -> pd.DataFrame:
        """Report missing values by column."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load() first.")
        
        missing = pd.DataFrame({
            'column': self.df.columns,
            'missing_count': self.df.isnull().sum().values,
            'missing_pct': (self.df.isnull().sum() / len(self.df) * 100).values
        }).sort_values('missing_pct', ascending=False)
        
        return missing[missing['missing_count'] > 0]
    
    def handle_missing_values(self, strategy: str = "drop") -> pd.DataFrame:
        """
        Handle missing values.
        
        Args:
            strategy: 'drop' (rows), 'mean' (numerical), 'mode' (categorical)
        
        Returns:
            Cleaned dataframe
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load() first.")
        
        df_clean = self.df.copy()
        
        if strategy == "drop":
            df_clean = df_clean.dropna()
            logger.info(f"Dropped rows with NaN. Shape: {df_clean.shape}")
        
        elif strategy == "mean":
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        
        elif strategy == "mode":
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    mode_val = df_clean[col].mode()[0] if not df_clean[col].mode().empty else "Unknown"
                    df_clean[col].fillna(mode_val, inplace=True)
        
        return df_clean
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features for analysis.
        
        Args:
            df: Input dataframe
        
        Returns:
            Dataframe with additional features
        """
        df_feat = df.copy()
        
        # Loss Ratio
        df_feat['LossRatio'] = df_feat['TotalClaims'] / (df_feat['TotalPremium'] + 1e-6)
        
        # Margin
        df_feat['Margin'] = df_feat['TotalPremium'] - df_feat['TotalClaims']
        
        # Claim indicator
        df_feat['HasClaim'] = (df_feat['TotalClaims'] > 0).astype(int)
        
        # Policy duration (if date columns exist)
        if 'IssueDate' in df_feat.columns and 'ExpiryDate' in df_feat.columns:
            df_feat['IssueDate'] = pd.to_datetime(df_feat['IssueDate'], errors='coerce')
            df_feat['ExpiryDate'] = pd.to_datetime(df_feat['ExpiryDate'], errors='coerce')
            df_feat['PolicyDuration'] = (df_feat['ExpiryDate'] - df_feat['IssueDate']).dt.days
        
        logger.info(f"Created {len(df_feat.columns) - len(df.columns)} derived features")
        return df_feat


def load_and_prepare(data_path: str = "data/insurance_data.csv") -> pd.DataFrame:
    """
    Convenience function to load and prepare data in one call.
    
    Args:
        data_path: Path to insurance CSV
    
    Returns:
        Cleaned and feature-engineered dataframe
    """
    loader = InsuranceDataLoader(data_path)
    df = loader.load()
    df_clean = loader.handle_missing_values(strategy="drop")
    df_final = loader.create_derived_features(df_clean)
    
    return df_final


if __name__ == "__main__":
    # Example usage
    loader = InsuranceDataLoader("data/insurance_data.csv")
    df = loader.load()
    print(loader.check_missing_values())
