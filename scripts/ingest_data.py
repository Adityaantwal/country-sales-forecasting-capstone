"""Reproducible demonstration data ingestion. Replace generator with a real source connector as needed."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sales_monthly.csv"
COUNTRIES = ["Australia", "Brazil", "Canada", "Germany", "India", "United States"]

def build_dataset(seed=2026):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2018-01-01", "2024-12-01", freq="MS")
    rows = []
    scales = {"Australia": 85, "Brazil": 72, "Canada": 92, "Germany": 108, "India": 125, "United States": 160}
    for ci, country in enumerate(COUNTRIES):
        for ti, date in enumerate(dates):
            seasonal = 1 + 0.15 * np.sin(2 * np.pi * date.month / 12)
            trend = 1 + 0.006 * ti
            noise = rng.normal(1.0, 0.055)
            sales = max(1.0, scales[country] * seasonal * trend * noise)
            rows.append({"date": date.strftime("%Y-%m-%d"), "country": country, "sales": round(float(sales), 2)})
    return pd.DataFrame(rows)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = build_dataset()
    df.to_csv(OUT, index=False)
    print(f"Ingested {len(df)} monthly records to {OUT}")
    return df

if __name__ == "__main__":
    main()
