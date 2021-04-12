import boto3
import config.aws as aws_config


def view_capture_files(read_capture_file=False):
    s3_client = boto3.Session().client('s3')
    current_endpoint_capture_prefix = f'{aws_config.data_capture_prefix}/{aws_config.endpoint_name}'
    print(current_endpoint_capture_prefix)

    result = s3_client.list_objects(Bucket=aws_config.bucket, Prefix=current_endpoint_capture_prefix)
    capture_files = [capture_file.get("Key") for capture_file in result.get('Contents')]
    print("Found Capture Files:")
    print("\n ".join(capture_files))

    if read_capture_file:
        def get_obj_body(obj_key):
            return s3_client.get_object(Bucket=aws_config.bucket, Key=obj_key).get('Body').read().decode("utf-8")

        capture_file = get_obj_body(capture_files[-1])
        print(capture_file[:2000])


if __name__ == '__main__':
    view_capture_files(read_capture_file=True)
