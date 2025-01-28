import awswrangler as wr
import os

class AWSDBClient():

    def __init__(self, database_name, session):

        self.database_name = database_name
        self.session = session
        self.glue_client = session.client('glue')
        self.athena_s3_output_path = os.environ["ATHENA_S3_OUTPUT_PATH"]

    def query(self, query):

        return wr.athena.read_sql_query(
            sql = query,
            database = self.database_name,
            s3_output = self.athena_s3_output_path,
            boto3_session = self.session,
            ctas_approach = False
        )

    def get_schema_docs(self):

        # Fetch all tables in the DB
        database_tables = self.glue_client.get_tables(
            DatabaseName=self.database_name,
            NextToken=""
        )

        # Limit down to S3 Parquet tables
        s3_tables = [
            table_dict for table_dict in database_tables["TableList"] if table_dict["Parameters"]["classification"] == "parquet"
        ]

        # Generate the DB docs. Loop through each table
        db_docs = []
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
            db_docs.append(entry)

        return db_docs


