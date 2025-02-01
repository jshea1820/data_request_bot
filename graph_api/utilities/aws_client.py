import awswrangler as wr
import os
import boto3
import json

PARAM_NAMES = [
    "aws_access_key",
    "aws_access_secret_key",
    "aws_session_token",
    "aws_region",
    "glue_database_name",
    "athena_output_s3_bucket"
]

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
        self.param_group_name = os.environ["PARAM_GROUP_NAME"]
        self.db_doc_bucket = os.environ["DB_DOC_BUCKET"]

        self.database_name = None
        self.glue_database_name = None
        self.athena_output_s3_bucket = None
        self.user_account_session = None

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

    def load_database_info(self, database_name):

        self.database_name = database_name

        # Start by unpacking params and making a user session
        params = self._unpack_param_store()

        self.glue_database_name = params["glue_database_name"]
        self.athena_output_s3_bucket = params["athena_output_s3_bucket"]

        self.user_account_session = boto3.Session(
            aws_access_key_id=params["aws_access_key"],
            aws_secret_access_key=params["aws_access_secret_key"],
            aws_session_token=params["aws_session_token"],
            region_name=params["aws_region"]
        )

        # Use the user account session to create the schema document and save it locally
        schema_docs = self._get_schema_docs()
        self._save_schema_docs(schema_docs)

        # Load the user's documentation data from S3
        self._download_db_docs()

    def _unpack_param_store(self):

        params = {}
        ssm_client = self.app_role_session.client("ssm")

        for param_name in PARAM_NAMES:

            params[param_name] = ssm_client.get_parameter(
                Name=f"/{self.param_group_name}/{self.database_name}/{param_name}",
                WithDecryption=True
            )["Parameter"]["Value"]

        return params

    def _get_schema_docs(self):

        glue_client = self.user_account_session.client("glue")

        # Fetch all tables in the DB
        database_tables = glue_client.get_tables(
            DatabaseName=self.glue_database_name,
            NextToken=""
        )

        # Limit down to S3 Parquet tables
        s3_tables = [
            table_dict for table_dict in database_tables["TableList"] if table_dict["Parameters"]["classification"] == "parquet"
        ]

        # Generate the DB docs. Loop through each table
        schema_docs = []
        for table_dict in s3_tables:

            table_name = table_dict["Name"]
            table_column_info = table_dict["StorageDescriptor"]["Columns"]

            print("Sampling table {}".format(table_name))

            # Get a sample of 5 records from the table
            sample_query = """

            SELECT *
            FROM {}
            ORDER BY RAND()
            LIMIT 5

            """.format(table_name)

            sample_records_df = self.query(sample_query)

            # Turn everything to strings to make them serializable
            for col in sample_records_df.columns:
                sample_records_df[col] = sample_records_df[col].astype(str)

            sample_records = sample_records_df.to_dict(orient="records")

            # Create an entry with table name, column names and types, and sample entries
            entry = {
                "table_name": table_name,
                "columns": table_column_info,
                "sample_data": sample_records
            }
            schema_docs.append(entry)

        return schema_docs

    def query(self, query):

        return wr.athena.read_sql_query(
            sql = query,
            database = self.glue_database_name,
            s3_output = self.athena_output_s3_bucket,
            boto3_session = self.user_account_session,
            ctas_approach = False
        )

    def _save_schema_docs(self, schema_docs):

        # Write the schema doc to local storage
        doc_dir = f"./graph_api/graph_documents/{self.database_name}"
        doc_path = f"{doc_dir}/schema_doc.json"
        os.makedirs(doc_dir, exist_ok=True)
        with open(doc_path, "w") as json_file:
            json.dump(schema_docs, json_file, indent=4)

        return doc_path

    def _download_db_docs(self):

        s3_client = self.app_role_session.client("s3")

        # List all DB Doc files
        response = s3_client.list_objects_v2(
            Bucket=self.db_doc_bucket,
            Prefix=self.database_name
        )

        db_doc_file_keys = [obj["Key"] for obj in response["Contents"]]

        # Create a directory to download all the files into
        db_doc_dir = f"./graph_api/graph_documents/{self.database_name}/db_docs"
        os.makedirs(db_doc_dir, exist_ok=True)

        # Download all the DB Doc files
        for db_doc_file_key in db_doc_file_keys:

            file_name = db_doc_file_key.split("/")[-1]

            s3_client.download_file(
                self.db_doc_bucket,
                db_doc_file_key,
                f"{db_doc_dir}/{file_name}"
            )

