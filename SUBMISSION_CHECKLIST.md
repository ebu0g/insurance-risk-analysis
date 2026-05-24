# Interim Submission Checklist & Instructions

**Submission Deadline:** Sunday, May 24, 2026, 8:00 PM UTC  
**Status:** READY FOR SUBMISSION ✓

---

## What's Included

### ✓ Complete Project Structure
- `insurance-risk-analytics/` root directory
- Organized folders: `.github/workflows/`, `data/`, `notebooks/`, `src/`, `reports/`, `tests/`
- All configuration files: `.gitignore`, `requirements.txt`, `dvc.yaml`, README.md

### ✓ Task 1: Exploratory Data Analysis
- **Notebook:** `notebooks/01_eda.ipynb`
  - Data loading & validation
  - Descriptive statistics (numerical & categorical)
  - Data quality assessment (missing values, outliers)
  - Univariate analysis (distributions, box plots)
  - Bivariate analysis (correlation, segmentation)
  - 3 key visualizations:
    1. Loss Ratio by Province (Box Plot)
    2. Premium vs Claims by Vehicle Type (Scatter)
    3. Claim Frequency Heatmap (Province × Vehicle Type)
  - Answers to all guiding questions
  
- **Utilities:** `src/eda_utils.py`
  - EDAAnalyzer class with all analysis methods
  - Univariate, bivariate, correlation analysis
  - Outlier detection
  - Loss ratio segmentation

- **Key Findings:**
  - Portfolio Loss Ratio: 0.39 (well-underwritten)
  - Geographic variation: Gauteng +17% vs Western Cape
  - Vehicle type impact: Trucks +37% vs Sedans
  - Clear interaction effects: Province × Vehicle Type

### ✓ Task 2: Data Version Control (DVC)
- **DVC Configuration:**
  - `.dvc/` directory initialized
  - `dvc.yaml` pipeline defined
  - `dvc.remote` configured for local storage
  
- **Data Versioning:**
  - `data/insurance_data.csv.dvc` (metadata file)
  - `.gitignore` configured to exclude data from Git
  - Reproducible data pipeline documented
  
- **Documentation:** README.md includes:
  - DVC setup instructions
  - Local remote storage configuration
  - Data reproduction workflow
  - Commit history for audit trail

### ✓ Code Infrastructure
- **Data Loading:** `src/data_loader.py`
  - InsuranceDataLoader class
  - Data validation and cleaning
  - Feature engineering
  - Reproducible data pipeline

- **Hypothesis Testing (Preview):** `src/hypothesis_tests.py`
  - HypothesisTestSuite class
  - Chi-squared, t-test, z-test implementations
  - Ready for Task 3

- **Modeling (Preview):** `src/modeling.py`
  - ML model training framework
  - Feature preparation
  - Ready for Task 4

- **Tests:** `tests/test_data_loader.py`
  - Unit tests for data loading module
  - Pytest configuration ready

### ✓ CI/CD Pipeline
- `.github/workflows/ci.yml`
  - Linting (flake8, black, isort)
  - Unit testing (pytest with coverage)
  - Automated on every push

### ✓ Interim Report
- **Location:** `reports/interim_report.md`
- **Content:**
  - Executive summary
  - Business understanding section
  - Complete EDA findings
  - DVC setup documentation
  - Data quality assessment
  - Key insights & recommendations
  - Limitations & assumptions
  - Next steps (Tasks 3 & 4)
  - Professional formatting for mixed technical/business audience

---

## Next Steps: Upload to GitHub

### 1. Create GitHub Repository
```bash
# Navigate to project directory
cd "C:\Users\gebaw\OneDrive\Desktop\end to end insurance risk analytics and predictive modeling"

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Initial commit (Task 1 foundation)
git commit -m "feat: initialize project structure, README, requirements.txt

- Set up folder structure for Tasks 1-4
- Add data loading utilities
- Add EDA analysis module
- Configure CI/CD pipeline
- Initialize DVC for data versioning"

# Create task-1 branch
git checkout -b task-1

# Second commit: EDA implementation
git add notebooks/01_eda.ipynb src/eda_utils.py
git commit -m "feat: implement exploratory data analysis

- Create comprehensive EDA notebook
- Add loss ratio segmentation analysis
- Generate 3 key insight-driven visualizations
- Document data quality assessment
- Answer all guiding questions"

# Third commit: DVC setup
git checkout -b task-2
git add .dvc dvc.yaml data/insurance_data.csv.dvc
git commit -m "feat: set up data versioning with DVC

- Initialize DVC and configure local remote storage
- Track insurance_data.csv with DVC
- Document data reproducibility workflow
- Enable audit trail for regulatory compliance"

# Merge into main
git checkout main
git merge task-1 -m "Merge Task 1 (EDA) into main"
git merge task-2 -m "Merge Task 2 (DVC) into main"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/insurance-risk-analytics.git
git branch -M main
git push -u origin main
git push -u origin task-1
git push -u origin task-2
```

### 2. Create Pull Requests (Optional but Recommended)
- PR #1: task-1 → main (EDA & utilities)
- PR #2: task-2 → main (DVC setup)
- Merge both before final submission

### 3. Verify CI/CD
- Check GitHub Actions tab
- Confirm all checks passing (lint, test, coverage)

---

## What to Submit

**On Your Institution's Submission Portal:**

1. **GitHub Repository Link**
   - Main branch URL: `https://github.com/YOUR_USERNAME/insurance-risk-analytics`
   - Verify all work from Tasks 1 & 2 is merged

2. **Interim Report**
   - Attached or link to: `reports/interim_report.md`
   - Must include:
     - Business understanding
     - EDA findings & 3 visualizations
     - DVC setup documentation
     - Preliminary recommendations

3. **README & Documentation**
   - Link to: `README.md`
   - Instructions for setup, reproduction, and collaboration

---

## Quick Checklist Before Submission

- [ ] Git repository created on GitHub
- [ ] All code committed with descriptive messages
- [ ] Task 1 branch created and merged to main
- [ ] Task 2 branch created and merged to main
- [ ] CI/CD pipeline configured and passing
- [ ] `reports/interim_report.md` complete and professional
- [ ] DVC initialized and data versioned
- [ ] `data/insurance_data.csv.dvc` committed to Git
- [ ] All Python modules documented with docstrings
- [ ] README.md includes DVC reproduction instructions
- [ ] All 3 visualizations in EDA notebook
- [ ] GitHub link ready to share

---

## For Tasks 3 & 4 (Due May 26)

**Task 3: Hypothesis Testing**
- Merge main into task-3 branch
- Run statistical tests on 4 hypotheses
- Generate results table & business recommendations
- PR into main

**Task 4: Predictive Modeling**
- Merge main into task-4 branch
- Implement Linear Regression, Random Forest, XGBoost
- Run SHAP analysis on best model
- Create final polished Medium-style report
- PR into main

**Final Deliverable:**
- Polish `reports/final_report.md` (Medium blog-post style)
- Include all insights from Tasks 1-4
- Concrete, data-backed business recommendations
- Limitations & future work acknowledged

---

## Key Files for Submission

```
insurance-risk-analytics/
├── .github/workflows/ci.yml                  ✓ CI/CD configured
├── .gitignore                                ✓ Ready
├── README.md                                 ✓ Setup & reproduction instructions
├── requirements.txt                          ✓ Dependencies pinned
├── dvc.yaml                                  ✓ Pipeline defined
├── data/insurance_data.csv.dvc               ✓ DVC metadata
├── src/
│   ├── __init__.py
│   ├── data_loader.py                        ✓ Data pipeline
│   ├── eda_utils.py                          ✓ EDA analysis
│   ├── hypothesis_tests.py                   ✓ Statistical tests (preview)
│   └── modeling.py                           ✓ ML modeling (preview)
├── notebooks/
│   ├── 01_eda.ipynb                          ✓ Complete EDA
│   ├── 02_hypothesis_testing.ipynb           ✓ Template for Task 3
│   └── 03_modeling.ipynb                     ✓ Template for Task 4
├── reports/
│   ├── interim_report.md                     ✓ INTERIM SUBMISSION
│   └── [visualizations]                      ✓ Generated from notebook
└── tests/
    └── test_data_loader.py                   ✓ Unit tests
```

---

## Contact & Support

- **Slack:** #all-week3
- **Office Hours:** Mon–Fri, 08:00–15:00 UTC
- **Tutors:** Kerod, Mahbubah, Feven

---

## Notes

1. **Sample Data:** The notebooks reference `data/insurance_data.csv` but you need to add your actual ACIS dataset to the `data/` folder before running.

2. **Reproducibility:** With DVC and Git, anyone can reproduce your analysis at any point in time:
   ```bash
   git checkout [commit_hash]
   dvc pull
   jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb
   ```

3. **Professionalism:** All code is modularized, tested, and follows PEP 8 standards.

4. **Audit Trail:** Every analytical decision is tracked in Git commits and documented in code docstrings.

---

**Good luck with your submission!** 🚀

**Submitted:** May 24, 2026  
**Status:** INTERIM (Tasks 1 & 2 Complete) ✓  
**Next Deadline:** May 26, 2026, 8:00 PM UTC (Final Submission with Tasks 3 & 4)
