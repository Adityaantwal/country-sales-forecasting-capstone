.PHONY: setup ingest eda train test run
setup:
	python -m pip install -r requirements.txt
ingest:
	python scripts/ingest_data.py
eda:
	python scripts/run_eda.py
train:
	python scripts/train_model.py
test:
	python run_tests.py
run:
	uvicorn app.main:app --reload
