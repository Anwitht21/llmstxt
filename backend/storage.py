import hashlib
from typing import Callable
import boto3
from botocore.exceptions import ClientError
from config import settings

async def save_llms_txt(base_url: str, content: str, log: Callable) -> str | None:
    if not all([settings.r2_endpoint, settings.r2_access_key, settings.r2_secret_key, settings.r2_bucket]):
        log("Storage not configured, skipping upload")
        return None

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key,
            aws_secret_access_key=settings.r2_secret_key
        )

        url_hash = hashlib.md5(base_url.encode()).hexdigest()
        object_key = f"llms/{url_hash}.txt"

        s3_client.put_object(
            Bucket=settings.r2_bucket,
            Key=object_key,
            Body=content.encode(),
            ContentType='text/plain'
        )

        if settings.r2_public_domain:
            public_url = f"{settings.r2_public_domain}/{object_key}"
        else:
            public_url = f"{settings.r2_endpoint}/{settings.r2_bucket}/{object_key}"

        log(f"Uploaded to {public_url}")
        return public_url

    except ClientError as e:
        log(f"Storage error: {str(e)}")
        return None
