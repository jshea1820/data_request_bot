from shiny import ui, reactive
import os
import requests

from utils import extract_query_params
from graph_api_client import GraphAPIClient


# Create a welcome message
welcome_1 = ui.markdown(
    """
    Hi! I'm the data request bot. I can answer questions about your data.
    I don't yet have the ability to remember conversations, so please
    ask each question as an individual request.
    Please go easy on me, I'm still in beta.
    """
)

welcome_2 = ui.markdown(
    """
    I'll start with a quick summary of the data you uploaded to give you
    a sense of what's available. One moment please...
    """
)

app_chat_ui = ui.page_fillable(
    ui.panel_title("Data Request Bot"),
    ui.tags.a(
        ui.input_action_button("back_to_connect", "Set Connection"),
        href="/connect"
    ),
    ui.chat_ui("chat"),
    fillable_mobile=True,
)


def app_chat_server(input, output, session):

    chat = ui.Chat(id="chat", messages=[welcome_1, welcome_2])

    database_name = reactive.Value("")
    ready_to_send_initial_message = reactive.Value(False)
    initial_message_sent = reactive.Value(False)

    client = GraphAPIClient()

    @reactive.Effect
    def on_load():

        # Set the database name
        query_params = extract_query_params(session)
        database_name.set(query_params["database_name"])
        ready_to_send_initial_message.set(True)

    @reactive.Effect
    async def check_send_initial_message():
        if ready_to_send_initial_message.get() and not initial_message_sent.get():

            initial_message_sent.set(True)
            graph_response = client.get_initial_message(database_name.get())

            await chat.append_message_stream(graph_response)

    @chat.on_user_submit
    async def _():

        message = chat.user_input()

        graph_response = client.get_graph_response(database_name.get(), message)
        
        await chat.append_message(graph_response)

