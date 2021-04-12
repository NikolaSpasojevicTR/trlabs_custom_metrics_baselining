import config.aws as aws_config
from config.env_var import env
from sagemaker.processing import Processor, ProcessingInput, ProcessingOutput


def manual_monitor_process():
    # instead of waiting for an hour, we can manually start the processing job to already get some analysis results.
    # To do this we define a Processor object that takes the image URI of our custom image.
    # The input for our job will be the S3 location where captured inference requests and responses are stored,
    # and we'll output results to the same destination that the scheduled jobs write to.
    # This is for captured data as Input is jsonl

    processor = Processor(
        base_job_name='my-manual-mon',
        role=aws_config.role,
        image_uri=aws_config.baselining_repository_uri,
        instance_count=1,
        instance_type='ml.m5.xlarge',
        env=env,
    )

    processor.run(
        [ProcessingInput(
            input_name='endpointdata',
            source=aws_config.baseline_data_uri,
            destination='/opt/ml/processing/input_data',
        )],
        [ProcessingOutput(
            output_name='result',
            source='/opt/ml/processing/results',
            destination=aws_config.baseline_results_uri,
        )]
    )


if __name__ == '__main__':
    manual_monitor_process()


