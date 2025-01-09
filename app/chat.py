from shiny import App, ui, reactive, module

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

class AppChat:

    def __init__(self, app):

        self.app = app

        self.send_initial_message = reactive.Value(False)

        self.chat_app_ui = ui.page_fillable(
            ui.panel_title("Data Request Bot"),
            ui.tags.a(
                ui.input_action_button("back_to_upload", "Back to Data Upload"),
                href="/upload"
            ),
            ui.chat_ui("chat"),
            fillable_mobile=True,
        )

    def chat_app_server(self, input, output, session):
        self.chat = ui.Chat(id="chat", messages=[welcome_1, welcome_2])

        @self.chat.on_user_submit
        async def _():
            message = self.chat.user_input()

            response = self.app.graph.invoke(message)

            await self.chat.append_message(response)

        @reactive.Effect
        async def check_send_initial_message():

            if self.send_initial_message:
                self.send_initial_message.set(False)

                response = self.app.graph.get_initial_message()
                await self.chat.append_message_stream(response)
                await self.chat.append_message_stream("What else would you like to know?")
                


