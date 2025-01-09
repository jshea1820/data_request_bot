from shiny import App, ui

# Create a welcome message
welcome = ui.markdown(
    """
    Hi! I'm the data request bot. I can answer questions about your data.
    Please go easy on me, I'm still in beta.
    """
)

class AppChat:

    def __init__(self, app):

        self.app = app

        self.chat_app_ui = ui.page_fillable(
            ui.panel_title("Data Request Bot"),
            ui.chat_ui("chat"),
            fillable_mobile=True,
        )

    def chat_app_server(self, input, output, session):
        self.chat = ui.Chat(id="chat", messages=[welcome])

        @self.chat.on_user_submit
        async def _():
            message = self.chat.user_input()

            response = self.app.graph.invoke(message)

            await self.chat.append_message(response)

