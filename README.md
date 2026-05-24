# Insurance Risk Analytics & Predictive Modeling

A comprehensive data science project analyzing insurance claim patterns and building risk-based pricing models using ACIS insurance data.

## Project Overview

This project applies exploratory data analysis, statistical hypothesis testing, and machine learning to:
- Understand risk drivers across provinces, vehicle types, and demographics
- Build predictive models for claim frequency and severity
- Develop data-backed recommendations for dynamic pricing strategies

## Data Pipeline & Reproducibility

### Using DVC (Data Version Control)

Our data pipeline is tracked using **DVC**, enabling reproducible analysis and audit trails required in regulated industries.

#### Setup DVC Remote Storage

```bash
# Create local storage directory outside the project
mkdir C:\Users\gebaw\dvc-storage

# Optional but recommended: keep the local cache outside the repo too
mkdir C:\Users\gebaw\dvc-cache

# Configure DVC remote
dvc remote add -d localstorage C:\Users\gebaw\dvc-storage
dvc config cache.dir C:\Users\gebaw\dvc-cache
```

#### Reproduce the Data Pipeline

```bash
# Rebuild the cleaned dataset from the raw version
dvc repro prepare

# Push the tracked raw and cleaned versions to the local remote
dvc push

# Verify data is in place
ls data/
```

#### Track New Data Versions

```bash
# Track the raw dataset
dvc add data/insurance_data.csv

# After cleaning or updating the dataset, rerun the pipeline and push
dvc repro prepare
dvc push

# Commit the DVC metadata files
git add data/insurance_data.csv.dvc dvc.lock dvc.yaml .dvc/config .dvcignore
git commit -m "track data versions with DVC"
```

## Project Structure

```
insurance-risk-analytics/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI pipeline
├── data/                              # Tracked by DVC, not Git
│   ├── insurance_data.csv
│   └── .gitkeep
├── notebooks/
│   ├── 01_eda.ipynb                  # Exploratory Data Analysis
│   ├── 02_hypothesis_testing.ipynb   # Statistical hypothesis tests
│   └── 03_modeling.ipynb             # Predictive modeling
├── src/
│   ├── __init__.py
│   ├── data_loader.py                # Data loading utilities
│   ├── eda_utils.py                  # EDA visualization & analysis
│   ├── hypothesis_tests.py           # Statistical test functions
│   └── modeling.py                   # ML model training & evaluation
├── reports/
│   ├── interim_report.md             # Interim submission (Tasks 1-2)
│   └── final_report.md               # Final polished report
├── tests/
│   └── test_data_loader.py           # Unit tests
├── .dvc/                              # DVC configuration
├── .gitignore
├── dvc.yaml                          # DVC pipeline definition
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Installation & Setup

### 1. Clone Repository & Install Dependencies

```bash
git clone https://github.com/yourusername/insurance-risk-analytics.git
cd insurance-risk-analytics
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize DVC

```bash
dvc init
dvc remote add -d localstorage /path/to/local/storage
dvc pull  # Retrieve versioned data
```

### 3. Run Tests & Linting

```bash
pytest
flake8 src/
black src/
```

## Workflow & Git Branches

- **main** — stable, merged production branch
- **task-1** — EDA and data exploration
- **task-2** — DVC pipeline & data versioning
- **task-3** — Hypothesis testing
- **task-4** — Predictive modeling & SHAP interpretability

**Commit Workflow:**
```bash
git checkout -b task-1
# Make changes, commit regularly with descriptive messages
git commit -m "feat: add univariate analysis for premium distribution"
git push origin task-1
# Create Pull Request on GitHub
```

## Key Insights (From Task 1 & 2)

### Business Understanding
- **Loss Ratio (LR)** = Total Claims / Total Premiums; indicator of portfolio profitability
- **Claim Frequency** = Proportion of policies with ≥1 claim
- **Claim Severity** = Average claim amount given a claim occurred
- **Risk Segmentation** needed across provinces, vehicle types, and demographics for dynamic pricing

### EDA Findings
- *[See interim_report.md for detailed findings]*

### Data Quality
- Missing value strategy: [documented in notebooks]
- Outliers identified and flagged in key financial metrics

## CI/CD Pipeline

GitHub Actions automatically:
1. Runs pytest on all commits
2. Checks code style (flake8, black)
3. Validates DVC pipeline integrity
4. Reports coverage metrics

## Authors & Acknowledgments

**Tutors:** Kerod, Mahbubah, Feven  
**Institution:** [Your institution]  
**Submission Week:** May 20–26, 2026

## References

- [DVC Official Documentation](https://dvc.org/)
- [FSRAO Insurance Sector Resources](https://www.fsrao.ca/)
- [Insurance Analytics - UW-Madison](https://www.datascience.wisc.edu/)
- [SHAP: Explainable AI](https://shap.readthedocs.io/)

---

**Last Updated:** May 24, 2026  
**Status:** Interim Submission (Tasks 1 & 2 Complete)
