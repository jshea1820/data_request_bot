import boto3
import os

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

def save_parameters(
    database_name,
    parameters
):

    ssm_client = AWS_SESSION.client("ssm")
    param_group_name = os.environ["PARAM_GROUP_NAME"]

    print("Saving to parameter store...")

    for param_name in parameters:
        print(param_name)

        response = ssm_client.put_parameter(
            Name=f"/{param_group_name}/{database_name}/{param_name}",
            Value=parameters[param_name],
            Type="SecureString",
            Overwrite=True
        )
    
    print("Parameter store successful")


def extract_query_params(session):

    # Extract database details from query parameters
    query_string = session.input[".clientdata_url_search"]()[1:]

    query_param_strings = query_string.split("&")
    query_params = {
        query_param_string.split("=")[0]: query_param_string.split("=")[1] for query_param_string in query_param_strings
    }
    
    return query_params

