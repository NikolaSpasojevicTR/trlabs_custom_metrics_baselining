import random
import json
from datetime import datetime
from sagemaker.s3 import S3Uploader
import config.aws as aws_config


TEST_DATASET_SIZE = 600


def ground_truth_with_id(inference_id):
    random.seed(inference_id)  # to get consistent results
    rand = random.random()
    return {
        'groundTruthData': {
            'data': "1" if rand < 0.7 else "0", # randomly generate positive labels 70% of the time
            'encoding': 'CSV'
        },
        'eventMetadata': {
            'eventId': str(inference_id),
        },
        'eventVersion': '0',
    }


def upload_ground_truth(upload_time):
    records = [ground_truth_with_id(i) for i in range(TEST_DATASET_SIZE)]
    fake_records = [json.dumps(r) for r in records]
    data_to_upload = "\n".join(fake_records)
    target_s3_uri = f"{aws_config.ground_truth_upload_path}/{upload_time:%Y/%m/%d/%H/%M%S}.jsonl"
    print(f"Uploading {len(fake_records)} records to", target_s3_uri)
    S3Uploader.upload_string_as_file_body(data_to_upload, target_s3_uri)


def upload_last_hour():
    # Generate data for the last hour
    upload_ground_truth(
        datetime.utcnow() #- timedelta(hours=1)
    )


if __name__ == '__main__':
    upload_last_hour()
