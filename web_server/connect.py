from shiny import ui, reactive
from shiny import render


app_connect_ui = ui.page_fluid(
    ui.h2("Welcome to the Data Request Bot!"),
    ui.br(),
    ui.p(
        """
        The Data Request Bot is a chatbot for answering questions about your data without having to interact with a database
        or code in SQL at all. Using your uploaded database documentation, the chatbot can translate your natural language
        questions into executable SQL queries on your database, and use the results to come up with an answer.
        """
    ),
    ui.br(),
    ui.p(
        """
        To get started, please upload your database documentation (must be a Markdown .md file).
        If you don't have a database but would like a demo, download the sample DVD rentals database
        documentation at 
        """, 
        ui.a("this", href="https://github.com/jshea1820/data_request_bot/blob/main/example_data/DVD%20Rentals%20Database.md", target="_blank"),
        """ link. Then upload the file here."""
    ),
    ui.input_file(
        "db_doc_file_input", 
        "File upload",
        accept=".md"
    ),
    ui.output_ui("submit_button_1_ui"),
    ui.br(),
    ui.output_ui("db_archive_file_input_ui"),
    ui.output_ui("submit_button_2_ui"),
    ui.br()
)

def app_connect_server(input, output, session):

    # Reactive to hold the state of the current page
    current_page = reactive.Value("db_doc_upload_page")

    @reactive.Effect
    def on_load():
        print("Loading connect page...")

    # Reactive calculation to check if the DB doc has been uploaded
    @reactive.Calc
    def uploaded_db_doc_file():
        return input.db_doc_file_input()

    # Rendering for the first Submit button. Must have an uploaded file to render
    @render.ui
    def submit_button_1_ui():
        if not uploaded_db_doc_file():
            return None
        else:
            return ui.input_action_button("submit_button_1", "Submit")

    # Button click for first submission. Updates the page
    @reactive.Effect
    def submit_db_doc_file():
        if input.submit_button_1():
            files = uploaded_db_doc_file()
            current_page.set("db_archive_upload_page")

    # Rendering for the DB archive upload. Must be on the second page to render
    @render.ui
    def db_archive_file_input_ui():
        if current_page() == "db_doc_upload_page":
            return None
        else:
            return ui.div(
                ui.br(),
                ui.p(
                    """
                    Great! Next, we'll need your database. We do not yet support online database
                    connections, so we'll need the database as a Postgres archive (packaged in a
                    .zip file). If you're just here for the demo, you can download the DVD rentals
                    database archive 
                    """,
                    ui.a("here", href="https://github.com/jshea1820/data_request_bot/blob/main/example_data/dvdrental.zip", target="_blank"),
                    """, and then upload the .zip file to this page"""
                ),
                ui.input_file(
                    "db_archive_file_input",
                    "Upload file",
                    accept=".zip"
                )
            )
    
    # Reactive calculation to check if the archive has been uploaded
    @reactive.Calc
    def uploaded_db_archive_file():
        # Get the uploaded file(s) information
        return input.db_archive_file_input()

    # Rendering for the second submit button. We must have an uploaded archive file to render
    @render.ui
    def submit_button_2_ui():
        if not uploaded_db_archive_file():
            return None

        return ui.div(
            ui.p(
                """
                You're ready to start chatting! Click the button to proceed to the chat.
                It will take a few moments as we'll need to unpack your data and prepare
                the chatbot. Keep in mind this is still in beta and there may be bugs.
                """
            ),
            ui.tags.a(
                ui.input_action_button("submit_button_2", "Start Chatting"),
                href="/chat"
            )
        )

    # Button click for second submission. Runs the preparation
    @reactive.Effect
    def navigate_to_text_page():
        if input.submit_button_2():  # Button clicked

            files = uploaded_db_archive_file()

