from shiny import ui, reactive
from utils import AWS_SESSION, save_parameters

import os

app_landing_ui = ui.page_fluid(
    ui.panel_title("Data Request Bot"),
    ui.h4("Welcome to the Data Request Bot!"),
    ui.br(),
    ui.p(
        """
        The Data Request Bot is a chatbot for answering questions about your data without having to interact with a database
        or code in SQL at all. Simply connect the chatbot to your database, and ask it questions about your data.
        The chatbot can translate your natural language questions into executable SQL queries on your database, 
        and use the results to come up with an answer.
        """
    ),
    ui.h4("Getting Started"),
    ui.tags.a(
        ui.input_action_button("connect_button", "Set up a connection to your database"),
        href="/connect"
    ),
    ui.br(),
    ui.br(),
    ui.p("or"),
    ui.tags.a(
        ui.input_action_button("chat_button", "Start chatting now with some demo data"),
        href="/db_loading?database_name=demo"
    )
)

def app_landing_server(input, output, session):

    # Button click for submission
    @reactive.Effect
    def go_to_demo():
        if input.chat_button():

            database_name = "demo"

            session_credentials = AWS_SESSION.get_credentials()

            parameters = {
                "aws_access_key": session_credentials.access_key,
                "aws_access_secret_key": session_credentials.secret_key,
                "aws_session_token": session_credentials.token,
                "aws_region": os.environ["AWS_REGION"],
                "glue_database_name": os.environ["DEMO_AWS_GLUE_DATABASE"]
            }

            save_parameters(database_name, parameters)
