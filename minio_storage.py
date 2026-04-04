# storage.py
import boto3
import os
import tempfile
from botocore.exceptions import ClientError

# Same code works for MinIO and S3
# Just change the endpoint_url

def get_s3_client():
    endpoint = os.environ.get(
        "MINIO_ENDPOINT", "localhost:9000")
    access_key = os.environ.get(
        "MINIO_ACCESS_KEY", "admin")
    secret_key = os.environ.get(
        "MINIO_SECRET_KEY", "password123")

    return boto3.client(
        "s3",
        endpoint_url=f"http://{endpoint}",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1"
    )

BUCKET_NAME = os.environ.get(
    "MINIO_BUCKET", "ai-recruiter")

def ensure_bucket():
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket {BUCKET_NAME} ready")

def upload_file(file_bytes: bytes,
                filename: str) -> str:
    s3 = get_s3_client()
    import io
    s3.upload_fileobj(
        io.BytesIO(file_bytes),
        BUCKET_NAME,
        filename
    )
    # Return the S3 path
    return f"s3://{BUCKET_NAME}/{filename}"

def download_to_temp(s3_path: str) -> str:
    # s3_path = "s3://ai-recruiter/resume.pdf"
    filename = s3_path.split("/")[-1]
    suffix = "." + filename.split(".")[-1]

    s3 = get_s3_client()

    with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix) as tmp:
        s3.download_fileobj(
            BUCKET_NAME,
            filename,
            tmp
        )
        return tmp.name

def delete_file(filename: str):
    s3 = get_s3_client()
    try:
        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=filename
        )
    except ClientError:
        pass