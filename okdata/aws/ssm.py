import os

import boto3


def get_secret(key):
    """Return a secret (SecureString) from SSM stored under `key`.

    Depends on the environment variable `AWS_REGION` to determine the AWS
    region.

    Raises `botocore.exceptions.ClientError` if the parameter couldn't be
    fetched for some reason, such as missing permissions or that it doesn't
    exist.
    """
    client = boto3.client("ssm", region_name=os.environ["AWS_REGION"])
    response = client.get_parameter(Name=key, WithDecryption=True)
    return response["Parameter"]["Value"]
