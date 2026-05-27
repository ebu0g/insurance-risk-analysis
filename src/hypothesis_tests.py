"""Statistical Hypothesis Testing Framework."""

import logging
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats

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
            "hypothesis": f"H₀: No risk difference by {feature}",
            "test": "Chi-Squared",
            "feature": feature,
            "target": target,
            "chi2": round(chi2, 4),
            "p_value": round(p_value, 6),
            "dof": dof,
            "reject_h0": p_value < alpha,
            "alpha": alpha,
        }

        self.results.append(result)
        return result

    def ttest_independent(
        self, feature: str, target: str, group1: str, group2: str, alpha: float = 0.05
    ) -> Dict:
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
            "hypothesis": f"H₀: No {target} difference between {group1} and {group2}",
            "test": "Independent t-test",
            "feature": feature,
            "target": target,
            "group1": group1,
            "group2": group2,
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_value, 6),
            "mean_group1": round(group1_data.mean(), 2),
            "mean_group2": round(group2_data.mean(), 2),
            "reject_h0": p_value < alpha,
            "alpha": alpha,
        }

        self.results.append(result)
        return result

    def ztest_proportions(
        self, feature: str, target: str, group1: str, group2: str, alpha: float = 0.05
    ) -> Dict:
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

        z_stat, p_value = proportions_ztest(count, nobs, alternative="two-sided")

        result = {
            "hypothesis": f"H₀: No claim frequency difference between {group1} and {group2}",
            "test": "Two-Proportion z-test",
            "feature": feature,
            "target": target,
            "group1": group1,
            "group2": group2,
            "z_statistic": round(z_stat, 4),
            "p_value": round(p_value, 6),
            "prop_group1": round(group1_data.mean(), 3),
            "prop_group2": round(group2_data.mean(), 3),
            "reject_h0": p_value < alpha,
            "alpha": alpha,
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


def prepare_analysis_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataset with analysis-ready KPI columns."""
    analysis_df = df.copy()

    if "HasClaim" not in analysis_df.columns:
        analysis_df["HasClaim"] = (analysis_df["TotalClaims"] > 0).astype(int)

    if "Margin" not in analysis_df.columns:
        analysis_df["Margin"] = analysis_df["TotalPremium"] - analysis_df["TotalClaims"]

    if "ClaimSeverity" not in analysis_df.columns:
        analysis_df["ClaimSeverity"] = analysis_df["TotalClaims"].where(
            analysis_df["TotalClaims"] > 0
        )

    return analysis_df


def _decision(p_value: float, alpha: float) -> str:
    return "Reject H0" if p_value < alpha else "Fail to reject H0"


def _format_percentage(value: float) -> str:
    return f"{value:.1%}"


def compare_binary_kpi(
    df: pd.DataFrame,
    feature: str,
    group_a: str,
    group_b: str,
    *,
    alpha: float = 0.05,
    kpi: str = "HasClaim",
    hypothesis: str | None = None,
    business_question: str | None = None,
) -> Dict:
    """Run a chi-squared test on a binary KPI for two groups."""
    analysis_df = prepare_analysis_frame(df)
    subset = analysis_df[analysis_df[feature].isin([group_a, group_b])].copy()

    if subset.empty or subset[feature].nunique() < 2:
        raise ValueError(f"Need at least two comparable groups for {feature}.")

    contingency = pd.crosstab(subset[feature], subset[kpi]).reindex(
        index=[group_a, group_b],
        columns=[0, 1],
        fill_value=0,
    )

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    rate_a = subset.loc[subset[feature] == group_a, kpi].mean()
    rate_b = subset.loc[subset[feature] == group_b, kpi].mean()

    result = {
        "hypothesis": hypothesis
        or f"H0: No {kpi.lower()} difference between {group_a} and {group_b}",
        "business_question": business_question,
        "feature": feature,
        "group_a": group_a,
        "group_b": group_b,
        "kpi": kpi,
        "test": "Chi-squared test",
        "statistic": round(float(chi2), 4),
        "degrees_of_freedom": int(dof),
        "p_value": round(float(p_value), 6),
        "group_a_rate": round(float(rate_a), 3),
        "group_b_rate": round(float(rate_b), 3),
        "group_a_n": int((subset[feature] == group_a).sum()),
        "group_b_n": int((subset[feature] == group_b).sum()),
        "decision": _decision(float(p_value), alpha),
        "reject_h0": bool(p_value < alpha),
        "alpha": alpha,
    }

    if business_question:
        result["business_recommendation"] = (
            f"{business_question}: {group_a} rate is {_format_percentage(rate_a)} versus "
            f"{group_b} rate at {_format_percentage(rate_b)}."
        )

    result["contingency_table"] = contingency.to_dict()
    return result


def compare_numeric_kpi(
    df: pd.DataFrame,
    feature: str,
    group_a: str,
    group_b: str,
    *,
    alpha: float = 0.05,
    kpi: str = "Margin",
    hypothesis: str | None = None,
    business_question: str | None = None,
) -> Dict:
    """Run a Welch t-test on a numeric KPI for two groups."""
    analysis_df = prepare_analysis_frame(df)

    if kpi == "ClaimSeverity":
        group_a_values = analysis_df.loc[
            (analysis_df[feature] == group_a) & (analysis_df["TotalClaims"] > 0),
            "TotalClaims",
        ].dropna()
        group_b_values = analysis_df.loc[
            (analysis_df[feature] == group_b) & (analysis_df["TotalClaims"] > 0),
            "TotalClaims",
        ].dropna()
    else:
        group_a_values = analysis_df.loc[analysis_df[feature] == group_a, kpi].dropna()
        group_b_values = analysis_df.loc[analysis_df[feature] == group_b, kpi].dropna()

    if len(group_a_values) < 2 or len(group_b_values) < 2:
        raise ValueError(
            f"Need at least two observations per group for {feature} and {kpi}."
        )

    t_stat, p_value = stats.ttest_ind(group_a_values, group_b_values, equal_var=False)

    mean_a = float(group_a_values.mean())
    mean_b = float(group_b_values.mean())

    result = {
        "hypothesis": hypothesis
        or f"H0: No {kpi.lower()} difference between {group_a} and {group_b}",
        "business_question": business_question,
        "feature": feature,
        "group_a": group_a,
        "group_b": group_b,
        "kpi": kpi,
        "test": "Welch t-test",
        "statistic": round(float(t_stat), 4),
        "p_value": round(float(p_value), 6),
        "group_a_mean": round(mean_a, 2),
        "group_b_mean": round(mean_b, 2),
        "group_a_n": int(len(group_a_values)),
        "group_b_n": int(len(group_b_values)),
        "decision": _decision(float(p_value), alpha),
        "reject_h0": bool(p_value < alpha),
        "alpha": alpha,
    }

    if business_question:
        result["business_recommendation"] = (
            f"{business_question}: {group_a} average {kpi.lower()} is {mean_a:.2f} versus "
            f"{group_b} at {mean_b:.2f}."
        )

    return result


def build_business_recommendation(result: Dict) -> str:
    """Convert a test result into a concise business-facing recommendation."""
    if not result.get("reject_h0"):
        return (
            f"We fail to reject H0 for {result['feature']} ({result['p_value']:.3f}); "
            "no pricing change is warranted from this test alone."
        )

    feature = result["feature"]
    group_a = result["group_a"]
    group_b = result["group_b"]

    if result["kpi"] == "HasClaim":
        return (
            f"We reject H0 for {feature} ({result['p_value']:.3f}). {group_a} shows a "
            f"higher claim frequency than {group_b}, so a regional or segment-specific "
            "premium adjustment should be reviewed."
        )

    if result["kpi"] == "ClaimSeverity":
        return (
            f"We reject H0 for {feature} ({result['p_value']:.3f}). {group_a} has a "
            f"different claim severity profile than {group_b}, which supports targeted "
            "underwriting or excess-setting changes."
        )

    return (
        f"We reject H0 for {feature} ({result['p_value']:.3f}). The margin gap between "
        f"{group_a} and {group_b} suggests a targeted pricing review is warranted."
    )


def run_task3_analysis(df: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Run the four Task 3 hypothesis tests and return a results table."""
    analysis_df = prepare_analysis_frame(df)

    comparisons = [
        {
            "hypothesis": "H0: No risk differences across provinces",
            "business_question": "Province-level risk is being checked",
            "method": "binary",
            "feature": "Province",
            "group_a": "Gauteng",
            "group_b": "Western Cape",
            "kpi": "HasClaim",
        },
        {
            "hypothesis": "H0: No risk differences between zip codes",
            "business_question": "Zip-code-level claim frequency is being checked",
            "method": "binary",
            "feature": "ZipCodeCluster",
            "group_a": "2000-series",
            "group_b": "8000-series",
            "kpi": "HasClaim",
        },
        {
            "hypothesis": "H0: No significant margin difference between zip codes",
            "business_question": "Zip-code-level margin is being checked",
            "method": "numeric",
            "feature": "ZipCodeCluster",
            "group_a": "2000-series",
            "group_b": "8000-series",
            "kpi": "Margin",
        },
        {
            "hypothesis": "H0: No risk difference between Women and Men",
            "business_question": "Gender-based claim frequency is being checked",
            "method": "binary",
            "feature": "Gender",
            "group_a": "F",
            "group_b": "M",
            "kpi": "HasClaim",
        },
    ]

    def cluster_zipcode(zip_code: object) -> str | None:
        zip_text = str(zip_code)
        if zip_text.startswith("2"):
            return "2000-series"
        if zip_text.startswith("8"):
            return "8000-series"
        if zip_text.startswith("4"):
            return "4000-series"
        return None

    analysis_df["ZipCodeCluster"] = analysis_df["ZipCode"].apply(cluster_zipcode)

    if analysis_df["ZipCodeCluster"].isna().any():
        missing = sorted(
            analysis_df.loc[analysis_df["ZipCodeCluster"].isna(), "ZipCode"]
            .astype(str)
            .unique()
        )
        raise ValueError(
            "Zip-code clusters are incomplete in the sample data. Missing values: "
            + ", ".join(missing)
        )

    results: List[Dict] = []
    for item in comparisons:
        if item["method"] == "binary":
            result = compare_binary_kpi(
                analysis_df,
                item["feature"],
                item["group_a"],
                item["group_b"],
                alpha=alpha,
                kpi=item["kpi"],
                hypothesis=item["hypothesis"],
                business_question=item["business_question"],
            )
        else:
            result = compare_numeric_kpi(
                analysis_df,
                item["feature"],
                item["group_a"],
                item["group_b"],
                alpha=alpha,
                kpi=item["kpi"],
                hypothesis=item["hypothesis"],
                business_question=item["business_question"],
            )

        result["recommendation"] = build_business_recommendation(result)
        results.append(result)

    results_df = pd.DataFrame(results)
    ordered_columns = [
        "hypothesis",
        "business_question",
        "feature",
        "group_a",
        "group_b",
        "kpi",
        "test",
        "statistic",
        "p_value",
        "decision",
        "reject_h0",
        "group_a_rate",
        "group_b_rate",
        "group_a_mean",
        "group_b_mean",
        "group_a_n",
        "group_b_n",
        "recommendation",
    ]

    existing_columns = [
        column for column in ordered_columns if column in results_df.columns
    ]
    remaining_columns = [
        column for column in results_df.columns if column not in existing_columns
    ]
    return results_df[existing_columns + remaining_columns]


def run_standard_tests(df: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Backward-compatible wrapper for the Task 3 hypothesis tests."""
    return run_task3_analysis(df, alpha=alpha)


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
    if "HasClaim" not in df.columns:
        df["HasClaim"] = (df["TotalClaims"] > 0).astype(int)

    if "LossRatio" not in df.columns:
        df["LossRatio"] = df["TotalClaims"] / (df["TotalPremium"] + 1e-6)

    if "Margin" not in df.columns:
        df["Margin"] = df["TotalPremium"] - df["TotalClaims"]

    # Test 1: Risk differences by Province (Chi-squared on claim frequency)
    try:
        suite.chi_squared_test("Province", "HasClaim", alpha=alpha)
        logger.info("✓ Test 1: Province risk differences (Chi-squared)")
    except Exception as e:
        logger.error(f"✗ Test 1 failed: {e}")

    # Test 2: Risk differences by Gender
    try:
        suite.chi_squared_test("Gender", "HasClaim", alpha=alpha)
        logger.info("✓ Test 2: Gender risk differences (Chi-squared)")
    except Exception as e:
        logger.error(f"✗ Test 2 failed: {e}")

    # Test 3: Claim severity by Province (t-test)
    try:
        provinces = df["Province"].unique()
        if len(provinces) >= 2:
            suite.ttest_independent(
                "Province", "TotalClaims", provinces[0], provinces[1], alpha=alpha
            )
            logger.info("✓ Test 3: Claim severity by Province (t-test)")
    except Exception as e:
        logger.error(f"✗ Test 3 failed: {e}")

    # Test 4: Margin differences by Vehicle Type
    try:
        suite.chi_squared_test("VehicleType", "HasClaim", alpha=alpha)
        logger.info("✓ Test 4: Vehicle Type risk differences (Chi-squared)")
    except Exception as e:
        logger.error(f"✗ Test 4 failed: {e}")

    return suite.get_results_summary()


if __name__ == "__main__":
    # Example usage
    from data_loader import load_and_prepare

    df = load_and_prepare("data/insurance_data.csv")
    results = run_task3_analysis(df)
    print(results.to_string(index=False))
