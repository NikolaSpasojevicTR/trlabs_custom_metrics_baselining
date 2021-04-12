import json
import config.aws as aws_config
from sagemaker.model_monitor.monitoring_files import Statistics, Constraints


def view_constraints():
    """
    The constraint file is the file that is loaded by the model monitoring jobs to evaluate Model Quality Drift
    and detect inference violations
    """
    constraints = Constraints.from_s3_uri(constraints_file_s3_uri=aws_config.constraints_file_s3_uri)
    print(json.dumps(constraints.body_dict, default=str, indent=4, sort_keys=True))


if __name__ == '__main__':
    view_constraints()
