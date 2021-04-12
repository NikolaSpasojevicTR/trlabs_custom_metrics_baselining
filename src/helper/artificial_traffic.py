import boto3
from time import sleep
from threading import Thread
import config.aws as aws_config


def generate_artificial_traffic():
    runtime_client = boto3.client('runtime.sagemaker')

    def invoke_endpoint(endpoint_name, file_name):
        with open(file_name, 'r') as f:
            i = 0
            for row in f:
                payload = row.rstrip('\n')
                response = runtime_client.invoke_endpoint(
                    EndpointName=endpoint_name,
                    ContentType='text/csv',
                    Body=payload,
                    InferenceId=str(i),  # unique ID per row
                )["Body"].read()
                i += 1
                sleep(1)

    def invoke_endpoint_forever():
        while True:
            invoke_endpoint(aws_config.endpoint_name, 'data/test_data/test-dataset-input-cols.csv')

    thread = Thread(target=invoke_endpoint_forever)
    thread.start()


if __name__ == '__main__':
    generate_artificial_traffic()
