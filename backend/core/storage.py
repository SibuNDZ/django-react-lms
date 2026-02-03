from functools import lru_cache
import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _s3_client():
    return boto3.client(
        "s3",
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None),
        config=Config(signature_version=getattr(settings, "AWS_S3_SIGNATURE_VERSION", "s3v4")),
    )


def build_presigned_url(object_key, expires_in=None):
    """Return a presigned URL for a private S3 object key."""
    if not settings.USE_S3:
        return None
    bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
    if not bucket or not object_key:
        return None

    ttl = expires_in or getattr(settings, "AWS_QUERYSTRING_EXPIRE", 300)
    try:
        return _s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_key},
            ExpiresIn=ttl,
        )
    except ClientError as exc:
        logger.error("Failed to generate presigned URL: %s", exc)
        return None
