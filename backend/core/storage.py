from functools import lru_cache
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _s3_client():
    import boto3
    from botocore.client import Config
    return boto3.client(
        "s3",
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None),
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None) or None,
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None) or None,
        config=Config(
            signature_version=getattr(settings, "AWS_S3_SIGNATURE_VERSION", "s3v4"),
            s3={"addressing_style": getattr(settings, "AWS_S3_ADDRESSING_STYLE", "auto")},
        ),
    )


def build_presigned_url(object_key, expires_in=None):
    """Return a presigned URL for a private S3 object key."""
    if not getattr(settings, "USE_S3", False):
        return None
    bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
    if not bucket or not object_key:
        return None

    # FileField names are relative to the storage location prefix (AWS_LOCATION),
    # but the object key in the bucket includes it.
    location = (getattr(settings, "AWS_LOCATION", "") or "").strip("/")
    if location and not object_key.startswith(location + "/"):
        object_key = f"{location}/{object_key}"

    ttl = expires_in or getattr(settings, "AWS_QUERYSTRING_EXPIRE", 300)
    try:
        return _s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_key},
            ExpiresIn=ttl,
        )
    except Exception as exc:
        logger.error("Failed to generate presigned URL: %s", exc)
        return None
