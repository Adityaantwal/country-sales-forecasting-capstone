# Country Sales Forecasting API — Capstone Project

A GitHub-ready example business solution that predicts monthly sales for a specific country or for all countries combined. It includes automated data ingestion, EDA visualizations, baseline-vs-model comparison, a FastAPI prediction API, structured logging, lightweight performance monitoring, unit tests, and Docker support.

> **Data note:** This repository generates a deterministic synthetic dataset for demonstration. Replace it with the official/business dataset before making real-world claims. The included metrics describe only this synthetic dataset.

## Features mapped to the peer-review rubric

- **API unit tests:** `tests/test_api.py`
- **Model unit tests:** `tests/test_model.py`
- **Logging unit tests:** `tests/test_logging_utils.py`
- **Single test command:** `python run_tests.py`
- **Performance monitoring:** `GET /monitoring` returns request counts, error counts, average latency, and last prediction time.
- **Read/write isolation:** tests use temporary directories and a temporary model path; they do not modify production model or log files.
- **Country and aggregate predictions:** `GET /predict?country=India&months=3` and `GET /predict?months=3` (all countries combined).
- **Automated data ingestion:** `python scripts/ingest_data.py`
- **Multiple models compared:** naive seasonal baseline vs. Random Forest model in `scripts/train_model.py`; metrics saved to `reports/model_comparison.json`.
- **EDA visualizations:** `python scripts/run_eda.py`; charts saved under `reports/`.
- **Docker:** `Dockerfile` and `docker-compose.yml`.

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/ingest_data.py
python scripts/run_eda.py
python scripts/train_model.py
python run_tests.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## API examples

- One country: `http://127.0.0.1:8000/predict?country=India&months=3`
- All countries combined: `http://127.0.0.1:8000/predict?months=3`
- Available countries: `http://127.0.0.1:8000/countries`
- Health: `http://127.0.0.1:8000/health`
- Monitoring: `http://127.0.0.1:8000/monitoring`

`country` is optional. If omitted, the API sums country-level forecasts for the same future months.

## Data and modeling

The ingestion script creates a reproducible monthly dataset for six countries. The model uses country, month-of-year, trend, and lag features. A chronological holdout is used to compare a seasonal-naive baseline with a Random Forest regressor. The final model is fitted on all available observations after comparison.

## Repository layout

```text
app/
  main.py                 FastAPI routes and monitoring
  model.py                Load model and make forecasts
  logging_utils.py        JSON log configuration
  monitoring.py           In-memory request metrics
scripts/
  ingest_data.py          Reproducible synthetic data ingestion
  run_eda.py              EDA charts
  train_model.py          Baseline/model comparison and model export
tests/
  test_api.py
  test_model.py
  test_logging_utils.py
data/sales_monthly.csv
models/sales_model.joblib
reports/                  EDA charts and comparison JSON
Dockerfile
docker-compose.yml
run_tests.py
```

## Push to GitHub

Create an empty public GitHub repository, then run these commands from this folder:

```bash
git init
git add .
git commit -m "Build country sales forecasting API capstone"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Use the actual repository URL in the peer-review submission. Do not submit the example URL above.
