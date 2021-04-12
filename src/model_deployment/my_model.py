from sagemaker.predictor import CSVSerializer
from sagemaker.model import Model
import config.aws as aws_config
from config.data_capture import data_capture_config
import config.model as model_config


class MyModel:

    def __init__(self):
        self.model = Model(
            image_uri=model_config.image_uri,
            model_data=model_config.model_url,
            role=aws_config.role
        )

    #  PowerUser2 Prod privileges are needed in order to deploy to sagemaker and to allow DataCapture!!!
    def deploy(self):
        _ = self.model.deploy(
            initial_instance_count=1,
            instance_type='ml.m4.xlarge',  # specifies the instance type your inference model will run on
            endpoint_name=aws_config.endpoint_name,  # specifies the endpoint from which inference data will be captured from
            data_capture_config=data_capture_config,
            serializer=CSVSerializer()
        )
