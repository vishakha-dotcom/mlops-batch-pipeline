import argparse
import yaml
import pandas as pd
import numpy as np
import logging
import json
import time
import sys
import os
import csv


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def write_metrics(output_path, metrics):
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)


def load_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("Config file not found")

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception:
        raise Exception("Invalid YAML format")

    required_keys = ["seed", "window", "version"]
    for key in required_keys:
        if key not in config:
            raise Exception(f"Missing config key: {key}")

    return config


def load_data(input_path):
    if not os.path.exists(input_path):
        raise Exception("Input file not found")

    try:
       
        df = pd.read_csv(
            input_path,
            sep=",",
            quoting=csv.QUOTE_NONE,
            engine="python"
        )
    except Exception:
        raise Exception("Invalid CSV format")

    if df.empty:
        raise Exception("CSV is empty")


    df.columns = df.columns.str.strip().str.lower()

    logging.info(f"Columns found: {list(df.columns)}")

    if "close" not in df.columns:
        raise Exception("Missing 'close' column")

    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    setup_logging(args.log_file)

    start_time = time.time()

    try:
        logging.info("Job started")

        # Load config
        config = load_config(args.config)
        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        logging.info(f"Config loaded: seed={seed}, window={window}, version={version}")

        np.random.seed(seed)

        # Load data
        df = load_data(args.input)
        logging.info(f"Rows loaded: {len(df)}")

        # Rolling mean
        df["rolling_mean"] = df["close"].rolling(window=window).mean()
        logging.info(f"Rolling mean computed with window={window}")

        # Signal generation
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)

        # Drop initial NaN rows
        df = df.dropna()
        logging.info("Signal generated and NaN rows dropped")

        # Metrics
        rows_processed = len(df)
        signal_rate = df["signal"].mean()

        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": int(rows_processed),
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }

        logging.info(f"Metrics computed: {metrics}")

        write_metrics(args.output, metrics)

       
        print(json.dumps(metrics, indent=2))

        logging.info("Job completed successfully")

        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        logging.error(f"Error occurred: {str(e)}")

        write_metrics(args.output, error_metrics)

        print(json.dumps(error_metrics, indent=2))

        sys.exit(1)


if __name__ == "__main__":
    main()
