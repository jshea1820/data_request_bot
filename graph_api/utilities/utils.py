import os
import boto3

PARAM_NAMES = [
    "aws_access_key",
    "aws_access_secret_key",
    "aws_session_token",
    "aws_region",
    "glue_database_name"
]

def get_aws_session():
    ''' Assumes application role to create a session for subsequent AWS API calls '''

    # Start a Boto3 session using application credentials
    if os.environ["USE_AWS_CRED_ENV_VARS"] == "true":
        
        # Use credentials specified by env variables
        session = boto3.Session(
            aws_access_key_id=os.environ["APPLICATION_AWS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["APPLICATION_AWS_ACCESS_SECRET_KEY"],
            aws_session_token=os.environ["APPLICATION_AWS_SESSION_TOKEN"],
            region_name=os.environ["AWS_REGION"]
        )

    else:
        # Use whatever credentials the application can find
        session = boto3.Session()

    # Assume the application role
    sts_client = session.client("sts")
    role_arn = os.environ["APPLICATION_ROLE_ARN"]
    session_name = "MySession"

    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )

    # Return session generated from the credentials
    credentials = response["Credentials"]

    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=os.environ["AWS_REGION"]
    )

AWS_SESSION = get_aws_session()

def unpack_param_store(database_name, ssm_client):

    param_group_name = os.environ["PARAM_GROUP_NAME"]

    params = {}

    for param_name in PARAM_NAMES:

        params[param_name] = ssm_client.get_parameter(
            Name=f"/{param_group_name}/{database_name}/{param_name}",
            WithDecryption=True
        )["Parameter"]["Value"]

    return params
