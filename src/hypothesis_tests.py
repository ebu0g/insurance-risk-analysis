"""Statistical Hypothesis Testing Framework"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HypothesisTestSuite:
    """Framework for A/B hypothesis testing on insurance data."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize hypothesis test suite.
        
        Args:
            df: Input dataframe with insurance data
        """
        self.df = df
        self.results = []
        
    def chi_squared_test(self, feature: str, target: str, alpha: float = 0.05) -> Dict:
        """
        Chi-squared test for categorical feature vs categorical target.
        
        Args:
            feature: Grouping feature (e.g., 'Province')
            target: Binary target (e.g., 'HasClaim')
            alpha: Significance level
        
        Returns:
            Test result dictionary
        """
        contingency_table = pd.crosstab(self.df[feature], self.df[target])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        result = {
            'hypothesis': f"H₀: No risk difference by {feature}",
            'test': 'Chi-Squared',
            'feature': feature,
            'target': target,
            'chi2': round(chi2, 4),
            'p_value': round(p_value, 6),
            'dof': dof,
            'reject_h0': p_value < alpha,
            'alpha': alpha
        }
        
        self.results.append(result)
        return result
    
    def ttest_independent(self, feature: str, target: str, group1: str, group2: str, 
                         alpha: float = 0.05) -> Dict:
        """
        Independent samples t-test comparing two groups.
        
        Args:
            feature: Grouping feature (e.g., 'Province')
            target: Numeric target (e.g., 'TotalClaims')
            group1: First group value
            group2: Second group value
            alpha: Significance level
        
        Returns:
            Test result dictionary
        """
        group1_data = self.df[self.df[feature] == group1][target].dropna()
        group2_data = self.df[self.df[feature] == group2][target].dropna()
        
        t_stat, p_value = stats.ttest_ind(group1_data, group2_data)
        
        result = {
            'hypothesis': f"H₀: No {target} difference between {group1} and {group2}",
            'test': 'Independent t-test',
            'feature': feature,
            'target': target,
            'group1': group1,
            'group2': group2,
            't_statistic': round(t_stat, 4),
            'p_value': round(p_value, 6),
            'mean_group1': round(group1_data.mean(), 2),
            'mean_group2': round(group2_data.mean(), 2),
            'reject_h0': p_value < alpha,
            'alpha': alpha
        }
        
        self.results.append(result)
        return result
    
    def ztest_proportions(self, feature: str, target: str, group1: str, group2: str,
                         alpha: float = 0.05) -> Dict:
        """
        Two-proportion z-test for claim frequency.
        
        Args:
            feature: Grouping feature
            target: Binary target (0 or 1)
            group1: First group value
            group2: Second group value
            alpha: Significance level
        
        Returns:
            Test result dictionary
        """
        from statsmodels.stats.proportion import proportions_ztest
        
        group1_data = self.df[self.df[feature] == group1][target]
        group2_data = self.df[self.df[feature] == group2][target]
        
        count = np.array([group1_data.sum(), group2_data.sum()])
        nobs = np.array([len(group1_data), len(group2_data)])
        
        z_stat, p_value = proportions_ztest(count, nobs, alternative='two-sided')
        
        result = {
            'hypothesis': f"H₀: No claim frequency difference between {group1} and {group2}",
            'test': 'Two-Proportion z-test',
            'feature': feature,
            'target': target,
            'group1': group1,
            'group2': group2,
            'z_statistic': round(z_stat, 4),
            'p_value': round(p_value, 6),
            'prop_group1': round(group1_data.mean(), 3),
            'prop_group2': round(group2_data.mean(), 3),
            'reject_h0': p_value < alpha,
            'alpha': alpha
        }
        
        self.results.append(result)
        return result
    
    def get_results_summary(self) -> pd.DataFrame:
        """Return all test results as a DataFrame."""
        if not self.results:
            logger.warning("No tests have been run yet.")
            return pd.DataFrame()
        
        # Convert to DataFrame, handling variable columns
        results_df = pd.DataFrame(self.results)
        return results_df
    
    def export_results(self, filepath: str = "reports/hypothesis_results.csv") -> None:
        """Export results to CSV."""
        results_df = self.get_results_summary()
        results_df.to_csv(filepath, index=False)
        logger.info(f"Results exported to {filepath}")


def run_standard_tests(df: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """
    Run standard hypothesis tests for insurance risk analysis.
    
    Args:
        df: Input dataframe
        alpha: Significance level
    
    Returns:
        DataFrame of test results
    """
    suite = HypothesisTestSuite(df)
    
    # Ensure required features exist
    if 'HasClaim' not in df.columns:
        df['HasClaim'] = (df['TotalClaims'] > 0).astype(int)
    
    if 'LossRatio' not in df.columns:
        df['LossRatio'] = df['TotalClaims'] / (df['TotalPremium'] + 1e-6)
    
    if 'Margin' not in df.columns:
        df['Margin'] = df['TotalPremium'] - df['TotalClaims']
    
    # Test 1: Risk differences by Province (Chi-squared on claim frequency)
    try:
        suite.chi_squared_test('Province', 'HasClaim', alpha=alpha)
        logger.info("✓ Test 1: Province risk differences (Chi-squared)")
    except Exception as e:
        logger.error(f"✗ Test 1 failed: {e}")
    
    # Test 2: Risk differences by Gender
    try:
        suite.chi_squared_test('Gender', 'HasClaim', alpha=alpha)
        logger.info("✓ Test 2: Gender risk differences (Chi-squared)")
    except Exception as e:
        logger.error(f"✗ Test 2 failed: {e}")
    
    # Test 3: Claim severity by Province (t-test)
    try:
        provinces = df['Province'].unique()
        if len(provinces) >= 2:
            suite.ttest_independent('Province', 'TotalClaims', provinces[0], provinces[1], alpha=alpha)
            logger.info("✓ Test 3: Claim severity by Province (t-test)")
    except Exception as e:
        logger.error(f"✗ Test 3 failed: {e}")
    
    # Test 4: Margin differences by Vehicle Type
    try:
        suite.chi_squared_test('VehicleType', 'HasClaim', alpha=alpha)
        logger.info("✓ Test 4: Vehicle Type risk differences (Chi-squared)")
    except Exception as e:
        logger.error(f"✗ Test 4 failed: {e}")
    
    return suite.get_results_summary()


if __name__ == "__main__":
    # Example usage
    from data_loader import load_and_prepare
    
    df = load_and_prepare("data/insurance_data.csv")
    results = run_standard_tests(df)
    print(results)
