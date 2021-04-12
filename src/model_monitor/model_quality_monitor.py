from sagemaker.model_monitor import ModelQualityMonitor,CronExpressionGenerator, EndpointInput
from sagemaker.model_monitor.monitoring_files import Constraints
from sagemaker.model_monitor.dataset_format import DatasetFormat
from time import gmtime, strftime
from config.env_var import env
import config.aws as aws_config


class TrModelQualityMonitor:

    def __init__(self):
        self.model_quality_monitor = ModelQualityMonitor(
            role=aws_config.role,
            base_job_name=aws_config.baselining_repository_name,
            instance_count=1,
            instance_type='ml.m5.xlarge',
            volume_size_in_gb=20,
            max_runtime_in_seconds=1800,
            env=env  # Pass environment variables to the container
        )
        self.model_quality_monitor.image_uri = aws_config.baselining_repository_uri

        self.baseline_job = None

    def suggest_baseline(self):
        self.baseline_job = self.model_quality_monitor.suggest_baseline(
            baseline_dataset='{}/{}'.format(aws_config.baseline_data_uri, aws_config.baseline_dataset_name),
            problem_type='BinaryClassification',
            dataset_format=DatasetFormat.csv(header=True),
            output_s3_uri=aws_config.baseline_results_uri, # the baselining processing job will results in a constraints and statistics file on s3
            wait=True
        )

    def create_monitoring_schedule(self):
        self.model_quality_monitor.create_monitoring_schedule(
            monitor_schedule_name='DEMO-xgb-churn-pred-model-monitor-schedule-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime()),
            endpoint_input=EndpointInput(  # specify an endpoint input for a monitoring job
                endpoint_name=aws_config.endpoint_name, # specifies the endpoint from which inference data will be captured from
                probability_attribute="0",
                probability_threshold_attribute=0.8,
                destination='/opt/ml/processing/input_data'  # the destination of the input within the container
            ),
            problem_type='BinaryClassification',
            constraints=Constraints.from_s3_uri(constraints_file_s3_uri=aws_config.constraints_file_s3_uri), # utilise the constraints file (generated from the baseline job) to run a monitoring job
            ground_truth_input=aws_config.ground_truth_upload_path, # labeled groundtruth data to be merged with the inference data
            output_s3_uri=aws_config.baseline_results_uri,  # output of merge job
            schedule_cron_expression=CronExpressionGenerator.hourly(),  # the merge job will be run once every hour!
        )


if __name__ == '__main__':
    tr_model_quality_monitor = TrModelQualityMonitor()
    tr_model_quality_monitor.suggest_baseline()
    tr_model_quality_monitor.create_monitoring_schedule()