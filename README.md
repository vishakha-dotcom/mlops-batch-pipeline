# MLOps Batch Pipeline Task

## Overview

This project implements a simple batch pipeline inspired by real-world MLOps workflows.
It reads market data (OHLCV), computes a rolling average on the closing price, and generates a binary signal based on that.

The goal was to keep the implementation minimal but reliable, with proper validation, logging, and reproducibility.

---

## What the script does

* Loads configuration from a YAML file
* Reads input data from a CSV file
* Validates input and handles common failure cases
* Computes rolling mean on the `close` column
* Generates a signal:

  * `1` if close > rolling mean
  * `0` otherwise
* Outputs:

  * Structured metrics (`metrics.json`)
  * Detailed logs (`run.log`)

---

## Reproducibility

The pipeline uses a fixed random seed from the config file to ensure deterministic results across runs.

---

## Handling edge cases

* Missing or invalid config file
* Missing input file
* Empty dataset
* Incorrect CSV format
* Missing `close` column

The program exits gracefully and still writes a metrics file in case of failure.

---

## Note on rolling mean

The first `(window - 1)` rows produce `NaN` values due to the rolling window.
These rows are excluded from signal computation to keep the results consistent.

---

## How to run (local)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the script:

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## How to run (Docker)

Build the image:

```bash
docker build -t mlops-task .
```

Run the container:

```bash
docker run --rm mlops-task
```

---

## Sample output

```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 43,
  "seed": 42,
  "status": "success"
}
```

---

## Project structure

```
mlops-task/
│
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
├── metrics.json
├── run.log
```

---

## Final thoughts

The focus here was not complexity, but clarity and reliability — making sure the pipeline behaves predictably and handles real-world issues like messy data and invalid inputs.

This setup can be extended further into a full pipeline with scheduling, monitoring, or model integration.
