# Marketing Campaign Analytics & ETL Pipeline

A beginner-friendly **Python + SQL data engineering portfolio project** aligned with marketing analytics use cases. It generates **synthetic** campaign data, validates it, calculates performance KPIs, loads it into a relational database, and presents an interactive Streamlit dashboard.

## Architecture

`Synthetic CSV files → Python/Pandas extraction → data-quality checks → KPI transformations → SQL database → SQL analysis + Streamlit dashboard`

**Stack:** Python, Pandas, SQLAlchemy, SQLite (default), optional MySQL, Streamlit, Plotly, pytest.

## Features
- Reproducible dataset: 5 campaigns × 60 days = 300 daily performance rows.
- Checks for missing columns/nulls, duplicate keys, invalid foreign keys, negative metrics, clicks greater than impressions, and conversions greater than clicks.
- Daily CTR, conversion rate, and cost per click; dashboard uses **weighted aggregate rates**.
- Full-refresh ETL (rerunnable without duplicate rows), SQL queries, channel filter, KPI cards, trend chart.
- No real customer information or credentials included.

## Run on Windows (PowerShell)

Install Python 3.10+ first. In the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_data.py
python etl.py
python -m pytest -q
python -m streamlit run dashboard.py
```

If PowerShell blocks activation, skip activation and use `.\.venv\Scripts\python.exe` instead of `python` for each command, and `.\.venv\Scripts\python.exe -m streamlit run dashboard.py` for the dashboard.

Streamlit prints a local URL (usually `http://localhost:8501`). Stop with Ctrl+C.

## Optional MySQL instead of SQLite

1. Create an empty database in MySQL Workbench:

```sql
CREATE DATABASE marketing_analytics;
```

2. In the **same PowerShell terminal** set a connection URL (replace placeholders; URL-encode special characters in passwords):

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/marketing_analytics"
python etl.py
python -m streamlit run dashboard.py
```

Do not commit passwords, `.env` files, or local databases. The default SQLite version requires no MySQL setup.

## Files

- `generate_data.py`: synthetic CSV source generator
- `etl.py`: extract, validation, transformation, load
- `dashboard.py`: interactive analytics UI
- `queries.sql`: campaign and daily KPI queries
- `tests/test_etl.py`: validation and metric tests
- `data/raw/`: generated input CSVs

## KPI definitions

- CTR (%) = total clicks / total impressions × 100
- Conversion rate (%) = total conversions / total clicks × 100
- CPC = spend / clicks
- Cost per conversion = spend / conversions
- Zero-denominator daily rates are reported as 0; SQL aggregate rates return NULL when denominator is 0.
