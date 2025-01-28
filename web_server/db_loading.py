from shiny import ui, reactive
from shiny import render
from utils import extract_query_params
from graph_api_client import GraphAPIClient

import os
import requests

app_db_loading_ui = ui.page_fluid(
    ui.panel_title("Data Request Bot"),
    ui.h4("Load database"),
    ui.p("""
    When you're ready, press the "Start Loading" button to begin loading the contents of the
    database into the chatbot. This may take a few minutes. 
    """),
    ui.output_ui("start_loading_button_ui"),
    ui.br(),
    ui.br(),
    ui.output_ui("loading_complete_text_ui"),
    ui.output_ui("start_chatting_button_ui"),
    ui.busy_indicators.use(),
    fillable_mobile=True,
)

def app_db_loading_server(input, output, session):

    client = GraphAPIClient()
    database_name = reactive.Value("")
    is_done_loading = reactive.Value(False)

    @reactive.Effect
    def on_load():

        query_params = extract_query_params(session)
        database_name.set(query_params["database_name"])

    @render.ui
    def start_loading_button_ui():

        return ui.input_action_button("start_loading", "Start Loading Database '{}'".format(database_name.get())),

    @reactive.Effect
    def _():
        if input.start_loading():

            client.load_graph(database_name.get())
            is_done_loading.set(True)

    @render.ui
    def loading_complete_text_ui():

        if is_done_loading.get():
            return ui.p("Loading complete!")
        else:
            return None

    @render.ui
    def start_chatting_button_ui():

        if is_done_loading.get():
            return ui.tags.a(
                ui.input_action_button("submit_button", "Start Chatting"),
                href="/chat?database_name={}".format(database_name.get())
            )
        
        else:
            return None
