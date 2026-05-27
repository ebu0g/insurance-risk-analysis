"""Predictive modeling and risk-based pricing helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor

logger = logging.getLogger(__name__)


@dataclass
class ModelComparison:
    """Container for fitted models and their evaluation table."""

    results: pd.DataFrame
    models: Dict[str, Pipeline]
    feature_columns: List[str]
    train_frame: pd.DataFrame
    test_frame: pd.DataFrame
    target_name: str


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create analysis-ready features for pricing and severity modeling."""
    model_df = df.copy()

    for column in ["IssueDate", "ExpiryDate"]:
        if column in model_df.columns:
            model_df[column] = pd.to_datetime(model_df[column], errors="coerce")

    if {"IssueDate", "ExpiryDate"}.issubset(model_df.columns):
        model_df["PolicyDurationDays"] = (
            model_df["ExpiryDate"] - model_df["IssueDate"]
        ).dt.days
        model_df["PolicyStartMonth"] = model_df["IssueDate"].dt.month
        model_df["PolicyEndMonth"] = model_df["ExpiryDate"].dt.month

    if "ZipCode" in model_df.columns:
        model_df["ZipPrefix"] = model_df["ZipCode"].astype(str).str[0]

    if "CustomValueEstimate" in model_df.columns:
        model_df["LogCustomValueEstimate"] = np.log1p(
            model_df["CustomValueEstimate"].clip(lower=0)
        )

    if {"TotalPremium", "PolicyDurationDays"}.issubset(model_df.columns):
        model_df["PremiumPerPolicyDay"] = model_df["TotalPremium"] / (
            model_df["PolicyDurationDays"].fillna(model_df["PolicyDurationDays"].median())
            + 1
        )

    if {"TotalClaims", "TotalPremium"}.issubset(model_df.columns):
        model_df["LossRatio"] = model_df["TotalClaims"] / (model_df["TotalPremium"] + 1e-6)
        model_df["Margin"] = model_df["TotalPremium"] - model_df["TotalClaims"]
        model_df["HasClaim"] = (model_df["TotalClaims"] > 0).astype(int)
        model_df["ClaimSeverity"] = model_df["TotalClaims"].where(model_df["TotalClaims"] > 0)

    return model_df


def _split_features_target(
    df: pd.DataFrame,
    target: str,
    exclude: List[str] | None = None,
    test_size: float = 0.3,
    random_state: int = 42,
    stratify: pd.Series | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split a modeling frame into train/test subsets."""
    drop_columns = set(exclude or []) | {target}
    X = df.drop(columns=[column for column in drop_columns if column in df.columns])
    y = df[target]

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Build a reusable preprocessing pipeline for numeric and categorical data."""
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = [column for column in X.columns if column not in numeric_features]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    transformers = []
    if numeric_features:
        transformers.append(("numeric", numeric_transformer, numeric_features))
    if categorical_features:
        transformers.append(("categorical", categorical_transformer, categorical_features))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def _fit_pipeline(
    preprocessor: ColumnTransformer,
    estimator,
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> Pipeline:
    """Fit a preprocessing + estimator pipeline."""
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", estimator),
        ]
    )
    pipeline.fit(X_train, y_train)
    return pipeline


def _regression_estimators(random_state: int = 42):
    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            random_state=random_state,
            n_jobs=-1,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=random_state,
            objective="reg:squarederror",
            tree_method="hist",
        ),
    }


def _classification_estimators(random_state: int = 42):
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=random_state,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=random_state,
            eval_metric="logloss",
            tree_method="hist",
        ),
    }


def train_severity_models(
    df: pd.DataFrame,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
) -> ModelComparison:
    """Fit and compare regression models for claim severity."""
    model_df = engineer_features(df)
    severity_df = model_df[model_df["TotalClaims"] > 0].copy()

    if len(severity_df) < 4:
        raise ValueError("Need at least four claim records to train severity models.")

    X_train, X_test, y_train, y_test = _split_features_target(
        severity_df,
        target="TotalClaims",
        exclude=["PolicyID", "HasClaim", "ClaimSeverity"],
        test_size=test_size,
        random_state=random_state,
    )

    preprocessor = build_preprocessor(X_train)
    results: List[Dict] = []
    fitted_models: Dict[str, Pipeline] = {}

    for model_name, estimator in _regression_estimators(random_state).items():
        pipeline = _fit_pipeline(preprocessor, estimator, X_train, y_train)
        predictions = pipeline.predict(X_test)

        rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
        r2 = float(r2_score(y_test, predictions))

        results.append(
            {
                "model": model_name,
                "rmse": round(rmse, 4),
                "r2": round(r2, 4),
            }
        )
        fitted_models[model_name] = pipeline

    results_df = pd.DataFrame(results).sort_values(["rmse", "r2"], ascending=[True, False])

    return ModelComparison(
        results=results_df,
        models=fitted_models,
        feature_columns=X_train.columns.tolist(),
        train_frame=X_train,
        test_frame=X_test,
        target_name="TotalClaims",
    )


def train_claim_probability_models(
    df: pd.DataFrame,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
) -> ModelComparison:
    """Fit and compare classification models for claim probability."""
    model_df = engineer_features(df)

    if "HasClaim" not in model_df.columns:
        model_df["HasClaim"] = (model_df["TotalClaims"] > 0).astype(int)

    X_train, X_test, y_train, y_test = _split_features_target(
        model_df,
        target="HasClaim",
        exclude=["PolicyID", "TotalClaims", "ClaimSeverity"],
        test_size=test_size,
        random_state=random_state,
        stratify=model_df["HasClaim"],
    )

    preprocessor = build_preprocessor(X_train)
    results: List[Dict] = []
    fitted_models: Dict[str, Pipeline] = {}

    for model_name, estimator in _classification_estimators(random_state).items():
        pipeline = _fit_pipeline(preprocessor, estimator, X_train, y_train)
        predictions = pipeline.predict(X_test)

        results.append(
            {
                "model": model_name,
                "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
                "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
                "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
            }
        )
        fitted_models[model_name] = pipeline

    results_df = pd.DataFrame(results).sort_values(["f1", "accuracy"], ascending=[False, False])

    return ModelComparison(
        results=results_df,
        models=fitted_models,
        feature_columns=X_train.columns.tolist(),
        train_frame=X_train,
        test_frame=X_test,
        target_name="HasClaim",
    )


def get_feature_names(pipeline: Pipeline) -> List[str]:
    """Extract transformed feature names from a fitted pipeline."""
    preprocessor = pipeline.named_steps["preprocessor"]
    return preprocessor.get_feature_names_out().tolist()


def _transformed_frame(pipeline: Pipeline, X: pd.DataFrame) -> np.ndarray:
    """Transform raw features with the fitted preprocessor."""
    return pipeline.named_steps["preprocessor"].transform(X)


def explain_with_shap(
    pipeline: Pipeline,
    X_train: pd.DataFrame,
    X_explain: pd.DataFrame,
    *,
    output_path: str | Path,
    top_n: int = 10,
) -> pd.DataFrame:
    """Create SHAP summary outputs for a fitted pipeline and save a bar plot."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    feature_names = get_feature_names(pipeline)
    model = pipeline.named_steps["model"]
    transformed_train = _transformed_frame(pipeline, X_train)
    transformed_explain = _transformed_frame(pipeline, X_explain)

    if hasattr(model, "feature_importances_"):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(transformed_explain)
        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
    elif hasattr(model, "coef_"):
        explainer = shap.Explainer(model, transformed_train)
        shap_values = explainer(transformed_explain).values
    else:
        explainer = shap.Explainer(model, transformed_train)
        shap_values = explainer(transformed_explain).values

    if shap_values.ndim == 1:
        shap_values = shap_values.reshape(-1, 1)

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "mean_abs_shap": np.abs(shap_values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)

    top_features = importance.head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features["feature"].iloc[::-1], top_features["mean_abs_shap"].iloc[::-1])
    plt.title("Top SHAP Feature Importance")
    plt.xlabel("Mean |SHAP value|")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return top_features


def explain_top_features_business_terms(feature_importance: pd.DataFrame) -> List[str]:
    """Turn feature importance into concise business interpretations."""
    interpretations = []
    for _, row in feature_importance.iterrows():
        feature = row["feature"]
        influence = row["mean_abs_shap"]
        interpretations.append(
            f"{feature} materially influences predicted claims; a one-unit change shifts the model output by about {influence:.4f} on average."
        )
    return interpretations


def score_risk_based_premium(
    df: pd.DataFrame,
    severity_pipeline: Pipeline,
    frequency_pipeline: Pipeline,
    *,
    expense_loading: float = 0.15,
    profit_margin: float = 0.20,
) -> pd.DataFrame:
    """Calculate risk-based premium recommendations for each policy."""
    model_df = engineer_features(df)
    scoring_df = model_df.copy()

    X = scoring_df.drop(
        columns=[column for column in ["PolicyID", "TotalClaims", "ClaimSeverity"] if column in scoring_df.columns]
    )

    claim_probability = frequency_pipeline.predict_proba(X)[:, 1]
    predicted_severity = severity_pipeline.predict(X)
    expected_claim = claim_probability * predicted_severity
    recommended_premium = expected_claim * (1 + expense_loading + profit_margin)

    output = scoring_df[[column for column in ["PolicyID", "TotalPremium", "TotalClaims"] if column in scoring_df.columns]].copy()
    output["ClaimProbability"] = claim_probability
    output["PredictedSeverity"] = predicted_severity
    output["ExpectedClaim"] = expected_claim
    output["RecommendedPremium"] = recommended_premium
    output["ExpenseLoading"] = expense_loading
    output["ProfitMargin"] = profit_margin
    return output


def run_modeling_workflow(
    df: pd.DataFrame,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
    shap_output_path: str | Path = "reports/shap_summary.png",
) -> Dict[str, object]:
    """Run the full Task 4 modeling and pricing workflow."""
    severity_comparison = train_severity_models(
        df,
        test_size=test_size,
        random_state=random_state,
    )
    frequency_comparison = train_claim_probability_models(
        df,
        test_size=test_size,
        random_state=random_state,
    )

    best_severity_model_name = severity_comparison.results.iloc[0]["model"]
    best_severity_model = severity_comparison.models[best_severity_model_name]

    feature_importance = explain_with_shap(
        best_severity_model,
        severity_comparison.train_frame,
        severity_comparison.test_frame,
        output_path=shap_output_path,
        top_n=10,
    )

    pricing_frame = score_risk_based_premium(
        df,
        severity_pipeline=best_severity_model,
        frequency_pipeline=frequency_comparison.models[frequency_comparison.results.iloc[0]["model"]],
    )

    return {
        "severity_comparison": severity_comparison.results,
        "frequency_comparison": frequency_comparison.results,
        "best_severity_model_name": best_severity_model_name,
        "best_severity_model": best_severity_model,
        "best_frequency_model_name": frequency_comparison.results.iloc[0]["model"],
        "best_frequency_model": frequency_comparison.models[frequency_comparison.results.iloc[0]["model"]],
        "feature_importance": feature_importance,
        "pricing_frame": pricing_frame,
    }