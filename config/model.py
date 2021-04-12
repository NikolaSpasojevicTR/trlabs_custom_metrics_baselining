import boto3
from time import gmtime, strftime
from sagemaker.amazon.amazon_estimator import get_image_uri
import config.aws as aws_config


model_url = 's3://{}/{}/model/xgb-churn-prediction-model.tar.gz'.format(aws_config.default_bucket, aws_config.prefix)
model_name = "DEMO-xgb-churn-pred-model-monitor-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
image_uri = get_image_uri(boto3.Session().region_name, 'xgboost', '0.90-1')
endpoint_name = 'DEMO-xgb-churn-pred-model-monitor-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
