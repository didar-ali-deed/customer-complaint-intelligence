# AGENTS.md

## Project
Customer Complaint Intelligence Platform

This repository is an end-to-end data analytics portfolio project using the CFPB Consumer Complaint Database.

The goal is to build a professional, reproducible analytics pipeline using Python, SQL, NLP, SQLite, Git, and Power BI preparation.

The final Power BI `.pbix` file will be built manually by the user.

---

## Core Instructions

- Do not ask the user questions unless absolutely blocked by missing credentials or inaccessible resources.
- Make sensible professional decisions independently.
- Continue working until all automatable work is complete.
- Do not stop after partial implementation.
- Fix errors encountered during execution.
- Do not fabricate data, metrics, findings, or project results.
- Derive all reported statistics from actual processed data.
- Prefer official CFPB data sources.
- Do not switch to Kaggle unless the official CFPB source is unavailable.

---

## Main Dataset

Use the official CFPB Consumer Complaint Database.

Official source:

https://www.consumerfinance.gov/data-research/consumer-complaints/

Use the complete dataset available at execution time.

Preserve the raw source data unchanged.

If the source is compressed:

1. Download automatically.
2. Save the original archive.
3. Extract automatically.
4. Keep the raw extracted source unchanged.

Create source metadata including:

- source URL
- download date
- filename
- file size
- SHA-256 hash where practical
- row count
- source description

---

## Technology Stack

Primary technologies:

- Python
- Pandas
- NumPy
- SQLite
- SQL
- Matplotlib
- Jupyter
- Power BI preparation
- Git

Optional lightweight libraries:

- requests
- tqdm
- pyarrow
- scikit-learn
- nltk
- wordcloud

Avoid unnecessary dependencies.

Do not introduce Spark unless the dataset genuinely requires it.

---

## Coding Standards

Use:

- Python 3
- `pathlib`
- functions instead of monolithic scripts
- type hints where useful
- docstrings
- logging
- clear variable names
- modular architecture
- reusable utilities
- defensive error handling

Avoid:

- hardcoded absolute paths
- giant scripts
- duplicate logic
- unexplained magic numbers
- unnecessary DataFrame copies
- silent failures
- fake placeholder outputs

Prefer Parquet for large intermediate datasets.

Use chunked processing if memory is constrained.

---

## Repository Structure

Maintain approximately this structure:

```text
customer-complaint-intelligence/
├── AGENTS.md
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── powerbi/
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   └── 03_narrative_analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── download_data.py
│   ├── inspect_data.py
│   ├── clean_data.py
│   ├── feature_engineering.py
│   ├── build_database.py
│   ├── sql_analysis.py
│   ├── narrative_analysis.py
│   ├── export_powerbi.py
│   ├── validate_outputs.py
│   └── run_pipeline.py
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_data_quality.sql
│   ├── 03_core_analysis.sql
│   ├── 04_company_analysis.sql
│   ├── 05_product_analysis.sql
│   ├── 06_geographic_analysis.sql
│   ├── 07_time_analysis.sql
│   └── 08_powerbi_views.sql
│
├── database/
│   └── complaints.db
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── reports/
│   └── logs/
│
├── powerbi/
│   ├── POWER_BI_BUILD_GUIDE.md
│   ├── POWER_BI_MEASURES.md
│   ├── POWER_BI_MODEL.md
│   └── POWER_BI_VISUAL_PLAN.md
│
└── docs/
    ├── DATA_DICTIONARY.md
    ├── PROJECT_ARCHITECTURE.md
    ├── BUSINESS_QUESTIONS.md
    ├── DATA_QUALITY_REPORT.md
    ├── ANALYSIS_FINDINGS.md
    └── PORTFOLIO_SUMMARY.md
```
