from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts.ingest_data import OUT, main as ingest

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

def main():
    if not OUT.exists():
        ingest()
    df = pd.read_csv(OUT, parse_dates=["date"])
    REPORTS.mkdir(exist_ok=True)
    # Chart 1: monthly sales by country
    plt.figure(figsize=(10, 5))
    for country, group in df.groupby("country"):
        plt.plot(group["date"], group["sales"], label=country, linewidth=1.5)
    plt.title("Monthly sales by country (synthetic dataset)")
    plt.xlabel("Month"); plt.ylabel("Sales units"); plt.legend(ncol=3, fontsize=8)
    plt.tight_layout(); plt.savefig(REPORTS / "sales_trend_by_country.png", dpi=150); plt.close()
    # Chart 2: sales distribution by country
    order = df.groupby("country")["sales"].mean().sort_values().index
    plt.figure(figsize=(9, 5))
    df.boxplot(column="sales", by="country", grid=False, rot=25)
    plt.suptitle(""); plt.title("Sales distribution by country"); plt.xlabel("Country"); plt.ylabel("Sales units")
    plt.tight_layout(); plt.savefig(REPORTS / "sales_distribution_by_country.png", dpi=150); plt.close()
    # Summary CSV
    df.groupby("country")["sales"].agg(["count", "mean", "median", "std", "min", "max"]).round(2).to_csv(REPORTS / "eda_summary.csv")
    print(f"EDA outputs saved in {REPORTS}")
if __name__ == "__main__":
    main()
