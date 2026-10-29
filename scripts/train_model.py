from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from scripts.ingest_data import main as ingest, OUT

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "sales_model.joblib"
METRICS_PATH = ROOT / "reports" / "model_comparison.json"
FEATURES = ["country", "month", "year", "time_index", "lag_count"]

def add_features(df):
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["month"] = data["date"].dt.month
    data["year"] = data["date"].dt.year
    data["time_index"] = (data["year"] - 2018) * 12 + data["month"]
    data["lag_count"] = data.groupby("country").cumcount()
    return data

def train_and_evaluate(data_path=OUT, model_path=MODEL_PATH, metrics_path=METRICS_PATH):
    data_path = Path(data_path)
    if not data_path.exists():
        ingest()
    df = add_features(pd.read_csv(data_path))
    # Chronological split: last 12 months per country are held out.
    train = df[df["date"] < "2024-01-01"]
    test = df[df["date"] >= "2024-01-01"]
    pre = ColumnTransformer([
        ("country", OneHotEncoder(handle_unknown="ignore"), ["country"]),
        ("numeric", "passthrough", ["month", "year", "time_index", "lag_count"])
    ])
    model = Pipeline([
        ("features", pre),
        ("regressor", RandomForestRegressor(n_estimators=180, max_depth=10, random_state=42, min_samples_leaf=2))
    ])
    model.fit(train[FEATURES], train["sales"])
    preds = model.predict(test[FEATURES])
    # Seasonal-naive baseline: previous year's same month for each country.
    baseline = []
    for row in test.itertuples(index=False):
        prev = df[(df["country"] == row.country) & (df["date"] == row.date - pd.DateOffset(years=1))]
        baseline.append(float(prev.iloc[0]["sales"]) if len(prev) else float(train[train["country"] == row.country]["sales"].iloc[-1]))
    metrics = {
        "dataset_note": "Synthetic demonstration data; not official business data.",
        "holdout": "2024-01 through 2024-12 per country",
        "rows_train": int(len(train)),
        "rows_test": int(len(test)),
        "random_forest": {
            "MAE": round(float(mean_absolute_error(test["sales"], preds)), 4),
            "RMSE": round(float(np.sqrt(mean_squared_error(test["sales"], preds))), 4)
        },
        "seasonal_naive_baseline": {
            "MAE": round(float(mean_absolute_error(test["sales"], baseline)), 4),
            "RMSE": round(float(np.sqrt(mean_squared_error(test["sales"], baseline))), 4)
        }
    }
    model.fit(df[FEATURES], df["sales"])
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES}, model_path)
    Path(metrics_path).parent.mkdir(parents=True, exist_ok=True)
    Path(metrics_path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
