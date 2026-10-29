from pathlib import Path
import joblib
import numpy as np
import pandas as pd

COUNTRIES = ["Australia", "Brazil", "Canada", "Germany", "India", "United States"]
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "sales_model.joblib"
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sales_monthly.csv"

def load_bundle(model_path=DEFAULT_MODEL_PATH):
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}. Run python scripts/train_model.py first.")
    return joblib.load(path)

def make_features(country, date, history_count):
    date = pd.Timestamp(date)
    return pd.DataFrame([{
        "country": country,
        "month": int(date.month),
        "year": int(date.year),
        "time_index": int((date.year - 2018) * 12 + date.month),
        "lag_count": int(history_count),
    }])

def forecast_country(country, months=3, bundle=None, data_path=DATA_PATH):
    if country not in COUNTRIES:
        raise ValueError(f"Unknown country '{country}'. Choose one of: {', '.join(COUNTRIES)}")
    if not 1 <= int(months) <= 12:
        raise ValueError("months must be between 1 and 12")
    bundle = bundle or load_bundle()
    data = pd.read_csv(data_path, parse_dates=["date"])
    hist = data[data["country"] == country].sort_values("date")
    if hist.empty:
        raise ValueError(f"No historical data for {country}")
    last_date = hist["date"].max()
    last_value = float(hist.iloc[-1]["sales"])
    rows = []
    for step in range(1, int(months) + 1):
        future_date = last_date + pd.offsets.MonthBegin(step)
        features = make_features(country, future_date, len(hist))
        pred = float(bundle["model"].predict(features)[0])
        pred = max(0.0, pred)
        rows.append({"country": country, "date": future_date.strftime("%Y-%m-%d"), "predicted_sales": round(pred, 2)})
    return rows

def forecast_all(months=3, bundle=None, data_path=DATA_PATH):
    result = []
    for country in COUNTRIES:
        result.extend(forecast_country(country, months=months, bundle=bundle, data_path=data_path))
    grouped = {}
    for row in result:
        grouped[row["date"]] = grouped.get(row["date"], 0.0) + row["predicted_sales"]
    return [{"country": "ALL", "date": date, "predicted_sales": round(value, 2)}
            for date, value in sorted(grouped.items())]
