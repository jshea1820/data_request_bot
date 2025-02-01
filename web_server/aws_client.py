import os
import boto3

class AWSClient():

    def __init__(self):

        self.use_aws_cred_env_vars = os.environ["USE_AWS_CRED_ENV_VARS"] == "true"
        self.region = os.environ["AWS_REGION"]

        # Create a session using the application credentials
        if self.use_aws_cred_env_vars:

            self.app_cred_session = boto3.Session(
                aws_access_key_id=os.environ["APPLICATION_AWS_ACCESS_KEY"],
                aws_secret_access_key=os.environ["APPLICATION_AWS_ACCESS_SECRET_KEY"],
                aws_session_token=os.environ["APPLICATION_AWS_SESSION_TOKEN"],
                region_name=self.region
            )
        else:
            self.app_cred_session = boto3.Session()

        self.app_role_urn = os.environ["APPLICATION_ROLE_ARN"]
        self.aws_glue_demo_database = os.environ["DEMO_AWS_GLUE_DATABASE"]
        self.demo_db_doc_bucket = os.environ["DEMO_DB_DOC_BUCKET"]
        self.demo_db_doc_key = os.environ["DEMO_DB_DOC_KEY"]
        self.demo_athena_s3_output_bucket = os.environ["DEMO_ATHENA_S3_OUTPUT_BUCKET"]
        self.param_group_name = os.environ["PARAM_GROUP_NAME"]
        self.db_doc_bucket = os.environ["DB_DOC_BUCKET"]
        
        self.app_role_session = self._assume_application_role()

    def _assume_application_role(self):
        ''' Assumes role with required access and returns the session ''' 

        sts_client = self.app_cred_session.client("sts")
        session_name = "MySession"

        response = sts_client.assume_role(
            RoleArn=self.app_role_urn,
            RoleSessionName=session_name
        )

        credentials = response["Credentials"]

        return boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=self.region
        )

    def save_database_info(self, demo=True, database_name=None, parameters=None, db_doc_files=None):

        print("Saving DB info")

        # Overwrite parameters if we're using the demo
        if demo == True:
            print("Using demo params")
            database_name, parameters, db_doc_files = self._get_demo_info()

        print("Saving parameters")
        self._save_parameters(database_name, parameters)

        print("Saving files")
        self._save_db_docs(database_name, db_doc_files)
        
    def _get_demo_info(self):

        s3_client = self.app_role_session.client("s3")

        # Database name is demo
        database_name = "demo"

        # Parameters are based on the current session parameters
        session_credentials = self.app_role_session.get_credentials()
        parameters = {
            "aws_access_key": session_credentials.access_key,
            "aws_access_secret_key": session_credentials.secret_key,
            "aws_session_token": session_credentials.token,
            "aws_region": self.region,
            "glue_database_name": self.aws_glue_demo_database,
            "athena_output_s3_bucket": self.demo_athena_s3_output_bucket
        }

        s3_client.download_file(
            self.demo_db_doc_bucket,
            self.demo_db_doc_key,
            "./web_server/temp_assets/{}".format(self.demo_db_doc_key)
        )

        db_doc_files = [{
            "name": self.demo_db_doc_key,
            "datapath": "./web_server/temp_assets/{}".format(self.demo_db_doc_key)
        }]

        return (database_name, parameters, db_doc_files)

    def _save_parameters(self, database_name, parameters):

        ssm_client = self.app_role_session.client("ssm")

        print("Saving to parameter store...")

        for param_name in parameters:
            print(param_name)

            response = ssm_client.put_parameter(
                Name=f"/{self.param_group_name}/{database_name}/{param_name}",
                Value=parameters[param_name],
                Type="SecureString",
                Overwrite=True
            )
    
        print("Parameter store successful")

    def _save_db_docs(self, database_name, db_doc_files):

        s3_client = self.app_role_session.client("s3")

        for db_doc_file in db_doc_files:

            name = db_doc_file["name"]
            datapath = db_doc_file["datapath"]

            print("Saving {} to S3".format(name))

            s3_client.upload_file(datapath, self.db_doc_bucket, f"{database_name}/{name}")

