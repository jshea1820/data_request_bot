from shiny import App, ui, reactive, module
from shiny import render


class AppUpload:

    def __init__(self, app):

        self.app = app

        self.upload_app_ui = ui.page_fluid(
            ui.h2("Welcome to the data request bot!"),
            ui.input_file(
                "db_doc_file_input", 
                "To get started, please upload your database documentation (must be a Markdown .md file)",
                accept=".md"
            ),
            ui.output_ui("submit_button_1_ui"),
            ui.output_ui("db_archive_file_input_ui"),
            ui.output_ui("submit_button_2_ui"),
            ui.br()
        )

    def upload_app_server(self, input, output, session):

        # Reactive to hold the state of the current page
        current_page = reactive.Value("db_doc_upload_page")

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
                self.db_doc_file_name = files[0]["name"]
                self.db_doc_file_path = files[0]["datapath"]
                current_page.set("db_archive_upload_page")

        # Rendering for the DB archive upload. Must be on the second page to render
        @render.ui
        def db_archive_file_input_ui():
            if current_page() == "db_doc_upload_page":
                return None
            else:
                return ui.input_file(
                    "db_archive_file_input",
                    "Now please upload your Postgres database archive (must be a .zip file)",
                    accept=".zip"
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

            return ui.tags.a(
                ui.input_action_button("submit_button_2", "Start Chatting"),
                href="/chat"
            )

        # Button click for second submission. Runs the preparation
        @reactive.Effect
        def navigate_to_text_page():
            if input.submit_button_2():  # Button clicked

                files = uploaded_db_archive_file()
                self.db_archive_file_name = files[0]["name"]
                self.db_archive_file_path = files[0]["datapath"]

                self.app.prepare_for_chat() # Here is where the magic happens
