import pandas as pd
import pytest
from app.model import COUNTRIES, forecast_country, forecast_all

class DummyModel:
    def predict(self, frame):
        assert "country" in frame.columns
        return [100.0]

def test_forecast_country_returns_requested_months(tmp_path):
    dates = pd.date_range("2023-01-01", periods=12, freq="MS")
    data = pd.DataFrame({"date": dates, "country": ["India"]*12, "sales": [90.0]*12})
    path = tmp_path / "sales.csv"; data.to_csv(path, index=False)
    bundle = {"model": DummyModel()}
    result = forecast_country("India", 3, bundle=bundle, data_path=path)
    assert len(result) == 3
    assert all(row["country"] == "India" for row in result)
    assert all(row["predicted_sales"] >= 0 for row in result)

def test_invalid_country_rejected():
    with pytest.raises(ValueError, match="Unknown country"):
        forecast_country("Atlantis", 1, bundle={"model": DummyModel()})

def test_invalid_month_count_rejected():
    with pytest.raises(ValueError, match="months"):
        forecast_country("India", 13, bundle={"model": DummyModel()})

def test_forecast_all_aggregates_country_predictions(tmp_path):
    dates = pd.date_range("2023-01-01", periods=12, freq="MS")
    data = pd.concat([
        pd.DataFrame({"date": dates, "country": [c]*12, "sales": [90.0]*12})
        for c in COUNTRIES
    ])
    path=tmp_path/"sales.csv"; data.to_csv(path,index=False)
    result=forecast_all(2,bundle={"model":DummyModel()},data_path=path)
    assert len(result)==2
    assert all(row["country"]=="ALL" for row in result)
    assert all(row["predicted_sales"]==600.0 for row in result)
