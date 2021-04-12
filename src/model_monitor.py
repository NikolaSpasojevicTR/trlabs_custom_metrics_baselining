from sagemaker.model_monitor import ModelMonitor,CronExpressionGenerator, MonitoringOutput
from sagemaker.model_monitor.monitoring_files import Constraints, Statistics
from sagemaker.processing import ProcessingInput, ProcessingOutput
import config.aws as aws_config


class ModelQualityMonitor:

    def __init__(self):
        self.custom_baseline_monitor = ModelMonitor(
            role=aws_config.role,
            image_uri=aws_config.baselining_repository_uri,
            base_job_name=aws_config.baselining_repository_name,
            instance_count=1,
            instance_type='ml.m5.xlarge',
            volume_size_in_gb=20,
            max_runtime_in_seconds=3600,
            #This is an example to show how we can pass environment variables to the container
            env={
                'THRESHOLD': '0.15',
                'baseline_dataset_name': aws_config.baseline_dataset_name
            }
        )

        self.processing_output = ProcessingOutput(
            # output_name='result',
            source='/opt/ml/processing/results',
            destination=aws_config.baseline_results_uri
        )

    def suggest_baseline(self):
        self.custom_baseline_monitor.run_baseline(
            baseline_inputs=[
                ProcessingInput(
                    input_name='baseline_data',
                    source=aws_config.baseline_data_uri,
                    destination='/opt/ml/processing/input_data'
                )
            ],
            output=self.processing_output,
            wait=True,
            logs=True,
        )

    def create_monitoring_schedule(self):

        output = MonitoringOutput(source=self.processing_output.source, destination=self.processing_output.destination)

        self.custom_baseline_monitor.create_monitoring_schedule(
            monitor_schedule_name='custom-model-monitor',
            output=output,
            endpoint_input=aws_config.endpoint_name,
            schedule_cron_expression=CronExpressionGenerator.hourly(),
            # replace with your baseline constraints and statistics files
            constraints=Constraints.from_s3_uri(constraints_file_s3_uri=aws_config.constraints_file_s3_uri), # utilise the constraints file (generated from the baseline job) to run a monitoring job
            statistics=Statistics.from_s3_uri(statistics_file_s3_uri=aws_config.statistics_file_s3_uri)
        )
