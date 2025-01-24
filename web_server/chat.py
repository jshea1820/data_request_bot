from shiny import ui, reactive
import time

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

    @reactive.Effect
    def on_load():

        query_string = session.input[".clientdata_url_search"]()[1:]
        dataset_name = query_string.split("=")[1]
        print("Loading chat page...")
        print(dataset_name)
        # Here is where you load in the details for the graph
        print("Ok now I'm ready")


    @chat.on_user_submit
    async def _():
        message = chat.user_input()

        response = message # Replace this with API call

        await chat.append_message(response)
                


