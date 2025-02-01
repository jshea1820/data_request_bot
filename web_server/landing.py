from shiny import ui, reactive
from aws_client import AWSClient
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

    aws_client = AWSClient()

    # Button click for submission
    @reactive.Effect
    def go_to_demo():
        if input.chat_button():
            aws_client.save_database_info(demo=True)
