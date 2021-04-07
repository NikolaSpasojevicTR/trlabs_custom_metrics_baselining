"""
Custom Model Monitoring script for baselining
"""
import json
import os
import traceback
import csv
import argparse
from types import SimpleNamespace

from constraints import Constraints


def get_environment():
    """Load configuration variables for SM Model Monitoring job
    See https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-byoc-contract-inputs.html
    """
    try:
        with open("/opt/ml/config/processingjobconfig.json", "r") as conffile:
            defaults = json.loads(conffile.read())["Environment"]
    except Exception as e:
        traceback.print_exc()
        print("Unable to read environment vars from SM processing config file")
        defaults = {}

    return SimpleNamespace(
        dataset_format=os.environ.get(
            "dataset_format",
            defaults.get("dataset_format")
        ),
        dataset_source=os.environ.get(
            "dataset_source",
            defaults.get("dataset_source", "/opt/ml/processing/input_data"),
        ),
        end_time=os.environ.get(
            "end_time",
            defaults.get("end_time")
        ),
        output_path=os.environ.get(
            "output_path",
            defaults.get("output_path", "/opt/ml/processing/results"),
        ),
        publish_cloudwatch_metrics=os.environ.get(
            "publish_cloudwatch_metrics",
            defaults.get("publish_cloudwatch_metrics", "Enabled"),
        ),
        sagemaker_endpoint_name=os.environ.get(
            "sagemaker_endpoint_name",
            defaults.get("sagemaker_endpoint_name"),
        ),
        sagemaker_monitoring_schedule_name=os.environ.get(
            "sagemaker_monitoring_schedule_name",
            defaults.get("sagemaker_monitoring_schedule_name"),
        ),
        start_time=os.environ.get(
            "start_time",
            defaults.get("start_time")
        ),
        max_ratio_threshold=float(os.environ.get(
            "THRESHOLD",
            defaults.get("THRESHOLD", "nan"))
        ),
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline_dataset_name', type=str)
    args, _ = parser.parse_known_args()

    env = get_environment()
    print(f"Starting baselining with config:\n{env}")

    total_record_count = 0
    error_record_count = 0

    y_true = []
    y_pred = []

    dataset_source = env.dataset_source
    print(dataset_source)

    with open(os.path.join(dataset_source, args.baseline_dataset_name), "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_record_count += 1
            try:
                y_true.append(int(row['label']))
                y_pred.append(int(row['prediction']))
            except:
                error_record_count += 1
                continue

    print(f"validation file records: {total_record_count}")

    constraints = Constraints(y_true=y_true, y_pred=y_pred)
    baseline = constraints.suggest_baseline()
    print(baseline)

    errors = []
    if error_record_count > 0:
        errors.append({
            "feature_name": "Predictions",
            "constraint_check_type": "completeness_check",
            "description": "Could not read predictions for {} req/res pairs ({:.2f}% of total)".format(
                error_record_count,
                error_record_count * 100 / total_record_count,
            ),
        })
    print(f"Errors: {errors if len(errors) else 'None'}")

    print("Writing errors file...")
    with open(os.path.join(env.output_path, "errors.json"), "w") as outfile:
        outfile.write(json.dumps(
            {"errors": errors},
            indent=4,
        ))

    print("Writing overall constraints output...")
    with open(os.path.join(env.output_path, "constraints.json"), "w") as outfile:
        outfile.write(json.dumps(
            baseline,
            indent=4,
        ))

    print("Done")
