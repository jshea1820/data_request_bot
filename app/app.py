from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import RedirectResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from shiny import App, ui
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

import os

from upload import AppUpload
from chat import AppChat
from graph import Graph
from db_client import DBClient
from auth import BasicAuthBackend


class DataRequestApp:

    def __init__(self):

        self.app_upload = AppUpload(self)
        self.app_chat = AppChat(self)

        self.app_upload_actual = App(self.app_upload.upload_app_ui, self.app_upload.upload_app_server)
        self.app_chat_actual = App(self.app_chat.chat_app_ui, self.app_chat.chat_app_server)

    def prepare_for_chat(self):

        print("Preparing for chat...")

        db_name = self.app_upload.db_archive_file_name.split(".")[0]
        db_archive_path = self.app_upload.db_archive_file_path

        self.db_client = DBClient()
        self.db_client.create_database_from_archive(db_name, db_archive_path, "./app/app_data/database_archive")

        print("Moving the DB docs to local...")
        db_doc_file_name = self.app_upload.db_doc_file_name
        db_doc_file_path = self.app_upload.db_doc_file_path

        os.rename(db_doc_file_path, db_doc_file_name)
        print("DB docs moved")

        print("Connecting to restored database...")
        self.db_client.connect("app_user", "app_pass", db_name)

        self.graph = Graph(db_doc_file_name, self.db_client)
        self.graph.build_graph()
        self.graph.compile()

        self.app_chat.send_initial_message.set(True)


async def reroute_to_upload(request):
    return RedirectResponse(url='/upload')


def require_auth(route_function):
    async def wrapper(request: Request):
        if request.user.is_authenticated:
            return await route_function(request)
        else:
            # Force the browser to show the authentication prompt by returning 401 with the 'WWW-Authenticate' header
            return Response('Unauthorized', status_code=401, headers={'WWW-Authenticate': 'Basic realm="Restricted"'})

    return wrapper

data_request_app = DataRequestApp()

routes = [
    Route('/', require_auth(reroute_to_upload)),
    Mount('/upload', app=data_request_app.app_upload_actual),
    Mount('/chat', app=data_request_app.app_chat_actual)
]

app = Starlette(routes=routes)

USERNAME=os.environ["APP_USERNAME"]
PASSWORD=os.environ["APP_PASSWORD"]

app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend(USERNAME, PASSWORD))

