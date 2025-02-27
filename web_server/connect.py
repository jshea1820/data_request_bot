from shiny import ui, reactive
from shiny import render
import os

from aws_client import AWSClient


app_connect_ui = ui.page_fluid(
    ui.panel_title("Data Request Bot"),
    ui.h4("Database Connection"),
    ui.br(),
    ui.p(
        """
        Here is where you set the connection to your database. Currently only connections to
        AWS Glue Data Catalogs are support. Please DO NOT use AWS access keys and secret keys
        associated with AWS user profiles. Only use temporary credentials generated through
        the assumption of an AWS role that has permission to access the associated AWS Glue
        database.
        """
    ),
    ui.br(),
    ui.p(
        """
        If you'd like to proceed to chatting using the demo data, click here
        """
    ),
    ui.tags.a(
        ui.input_action_button("demo_data_button", "Use Demo Data"),
        href=f"/db_loading?database_name=demo"
    ),
    ui.br(),
    ui.br(),
    ui.input_text("database_name", "Name your database (does not have to the same as the AWS Glue database)"),
    ui.input_text("aws_access_key", "AWS Access Key"),
    ui.input_text("aws_access_secret_key", "AWS Access Secret Key"),
    ui.input_text("aws_session_token", "AWS Session Token"),
    ui.input_text("aws_region", "AWS Region (should be the region containing the Glue database)"),
    ui.input_text("glue_database_name", "AWS Glue Database Name"),
    ui.input_text("athena_output_s3_bucket", "S3 Bucket for Athena Query outputs"),
    ui.input_file("file_upload", "(Optional) Upload database documentation files", multiple=True),
    ui.output_ui("submit_button_ui"),
)

def app_connect_server(input, output, session):

    aws_client = AWSClient()

    # Demo data
    @reactive.Effect
    def go_to_demo():
        if input.demo_data_button():
            aws_client.save_database_info(demo=True)

    @render.ui
    def submit_button_ui():

        database_name = input.database_name()
        aws_access_key = input.aws_access_key()
        aws_access_secret_key = input.aws_access_secret_key()
        aws_session_token = input.aws_session_token()
        aws_region = input.aws_region()
        glue_database_name = input.glue_database_name()
        athena_output_s3_bucket = input.athena_output_s3_bucket()

        if database_name and aws_access_key and aws_access_secret_key and aws_session_token and glue_database_name and aws_region and athena_output_s3_bucket:

            return ui.tags.a(
                ui.input_action_button("submit_button", "Start Chatting"),
                href=f"/db_loading?database_name={database_name}"
            )
        else:
            return None

    # Button click for submission
    @reactive.Effect
    def submit():
        if input.submit_button():

            database_name = input.database_name()

            parameters = {
                "aws_access_key": input.aws_access_key(),
                "aws_access_secret_key": input.aws_access_secret_key(),
                "aws_session_token": input.aws_session_token(),
                "aws_region": input.aws_region(),
                "glue_database_name": input.glue_database_name(),
                "athena_output_s3_bucket": input.athena_output_s3_bucket()
            }

            db_doc_files = input.file_upload()

            aws_client.save_database_info(
                demo=False,
                database_name=database_name,
                parameters=parameters,
                db_doc_files=db_doc_files
            )
