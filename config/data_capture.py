from sagemaker.model_monitor import DataCaptureConfig
import config.aws as aws_config


# Configuration object passed in when deploying models to Amazon SageMaker Endpoints.
# This object specifies configuration related to endpoint data capture for use with Amazon SageMaker Model Monitoring.
data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri=aws_config.s3_capture_upload_path,
    capture_options=["Input", "Output"],  # specify to capture both request and response payload
    csv_content_types=["text/csv"],
    json_content_types=["application/json"]
)
