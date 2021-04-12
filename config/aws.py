import boto3
from sagemaker.amazon.amazon_estimator import get_image_uri
from time import gmtime, strftime


# aws profile
profile = {
    'aws_profile': 'tr-labs-prod',
    'aws_region': 'eu-west-1'
}


# workspace
workspace_id = 'ModelDrift'
role = 
region = boto3.Session().region_name
bucket = 'a204311-scw-euw1-modeldrift'


# data capture
prefix = 'sagemaker/DEMO-ModelMonitor'
data_capture_prefix = '{}/datacapture'.format(prefix)
s3_capture_upload_path = 's3://{}/{}'.format(bucket, data_capture_prefix)


# endpoint
endpoint_name = 'DEMO-xgb-churn-pred-model-monitor-2021-02-11-12-50-59'


# custom analyzer image (for baselining and monitoing) config
repository_arn = "arn:aws:ecr:eu-west-1:451191978663:repository/a204311-trlabs/model-monitor-baseline"
registry_id = "451191978663"
baselining_repository_name = 'model-monitor-baseline'
baselining_repository_uri = "451191978663.dkr.ecr.eu-west-1.amazonaws.com/a204311-trlabs/model-monitor-baseline"


# baselining file paths
baseline_dataset_name = 'validation_with_predictions.csv'
baseline_data_uri = 's3://a204311-scw-euw1-modeldrift/sagemaker/DEMO-ModelMonitor/baselining/data'
baseline_results_uri = 's3://a204311-scw-euw1-modeldrift/sagemaker/DEMO-ModelMonitor/baselining/results'


# groundtruth labels path
ground_truth_upload_path = 's3://a204311-scw-euw1-modeldrift/sagemaker/DEMO-ModelMonitor/ground_truth'


# constraints file path
constraints_file_s3_uri = 's3://a204311-scw-euw1-modeldrift/sagemaker/DEMO-ModelMonitor/baselining/results/constraints.json'