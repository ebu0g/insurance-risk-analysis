"""Exploratory Data Analysis Utilities"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class EDAAnalyzer:
    """Comprehensive EDA analysis toolkit."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize EDA analyzer.
        
        Args:
            df: Input dataframe for analysis
        """
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
    def summary_statistics(self) -> pd.DataFrame:
        """Generate descriptive statistics for numerical columns."""
        return self.df[self.numeric_cols].describe().round(2)
    
    def categorical_summary(self) -> Dict:
        """Summarize categorical columns."""
        summary = {}
        for col in self.categorical_cols:
            summary[col] = {
                'unique_values': self.df[col].nunique(),
                'value_counts': self.df[col].value_counts().to_dict(),
                'missing_pct': self.df[col].isnull().sum() / len(self.df) * 100
            }
        return summary
    
    def detect_outliers(self, column: str, method: str = "iqr") -> Tuple[int, List]:
        """
        Detect outliers using IQR or Z-score.
        
        Args:
            column: Column name
            method: 'iqr' or 'zscore'
        
        Returns:
            Tuple of (outlier_count, outlier_indices)
        """
        if column not in self.numeric_cols:
            raise ValueError(f"{column} is not numeric")
        
        data = self.df[column].dropna()
        
        if method == "iqr":
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = (data < lower_bound) | (data > upper_bound)
        
        elif method == "zscore":
            from scipy import stats
            z_scores = np.abs(stats.zscore(data))
            outliers = z_scores > 3
        
        else:
            raise ValueError("method must be 'iqr' or 'zscore'")
        
        outlier_indices = self.df[outliers].index.tolist()
        return outliers.sum(), outlier_indices
    
    def correlation_analysis(self, top_n: int = 10) -> pd.DataFrame:
        """
        Analyze correlations between numeric columns.
        
        Args:
            top_n: Return top N correlation pairs
        
        Returns:
            Sorted correlation pairs
        """
        corr_matrix = self.df[self.numeric_cols].corr()
        
        # Extract upper triangle
        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                pairs.append({
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j],
                    'correlation': corr_matrix.iloc[i, j]
                })
        
        pairs_df = pd.DataFrame(pairs).sort_values('correlation', key=abs, ascending=False)
        return pairs_df.head(top_n)
    
    def loss_ratio_analysis(self) -> pd.DataFrame:
        """
        Analyze loss ratio (TotalClaims / TotalPremium) by segmentation.
        
        Returns:
            Loss ratio summary by Province, VehicleType, Gender
        """
        if 'LossRatio' not in self.df.columns:
            self.df['LossRatio'] = self.df['TotalClaims'] / (self.df['TotalPremium'] + 1e-6)
        
        summaries = {}
        for col in ['Province', 'VehicleType', 'Gender']:
            if col in self.df.columns:
                summaries[col] = self.df.groupby(col).agg({
                    'LossRatio': ['mean', 'std', 'min', 'max'],
                    'TotalClaims': 'sum',
                    'TotalPremium': 'sum',
                    'PolicyID': 'count'  # count of policies
                }).round(3)
                summaries[col].columns = ['_'.join(col).strip() for col in summaries[col].columns.values]
        
        return summaries
    
    def plot_univariate(self, column: str, ax=None, bins: int = 30) -> plt.Axes:
        """Plot univariate distribution."""
        if column in self.numeric_cols:
            ax = sns.histplot(data=self.df, x=column, bins=bins, kde=True, ax=ax)
            ax.set_title(f"Distribution of {column}")
        elif column in self.categorical_cols:
            ax = sns.countplot(data=self.df, x=column, ax=ax)
            ax.set_title(f"Count by {column}")
            ax.tick_params(axis='x', rotation=45)
        
        return ax
    
    def plot_bivariate(self, x: str, y: str, ax=None) -> plt.Axes:
        """Plot bivariate relationship."""
        if x in self.numeric_cols and y in self.numeric_cols:
            ax = sns.scatterplot(data=self.df, x=x, y=y, alpha=0.6, ax=ax)
        elif x in self.categorical_cols and y in self.numeric_cols:
            ax = sns.boxplot(data=self.df, x=x, y=y, ax=ax)
        else:
            raise ValueError("Invalid column types for bivariate plot")
        
        ax.set_title(f"{y} by {x}")
        return ax
    
    def plot_correlation_matrix(self, ax=None) -> plt.Axes:
        """Plot correlation heatmap."""
        corr = self.df[self.numeric_cols].corr()
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)
        ax.set_title("Correlation Matrix - Numeric Features")
        return ax


if __name__ == "__main__":
    # Example usage
    from data_loader import load_and_prepare
    
    df = load_and_prepare("data/insurance_data.csv")
    analyzer = EDAAnalyzer(df)
    
    print("Summary Statistics:")
    print(analyzer.summary_statistics())
    
    print("\nTop Correlations:")
    print(analyzer.correlation_analysis())
