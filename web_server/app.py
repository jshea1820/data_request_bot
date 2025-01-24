from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import RedirectResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from shiny import App, ui
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response, PlainTextResponse

import os

from chat import app_chat_ui, app_chat_server
from connect import app_connect_ui, app_connect_server
from landing import app_landing_ui

from auth import BasicAuthBackend


async def reroute_to_landing(request):
    return RedirectResponse(url='/landing')


def require_auth(route_function):
    async def wrapper(request: Request):
        if request.user.is_authenticated:
            return await route_function(request)
        else:
            # Force the browser to show the authentication prompt by returning 401 with the 'WWW-Authenticate' header
            return Response('Unauthorized', status_code=401, headers={'WWW-Authenticate': 'Basic realm="Restricted"'})

    return wrapper

async def health_check(request):
    return PlainTextResponse("OK", status_code=200)

routes = [
    Route('/', require_auth(reroute_to_landing)),
    Route('/health', health_check),
    Mount('/landing', app=App(app_landing_ui, None)),
    Mount('/connect', app=App(app_connect_ui, app_connect_server)),
    Mount('/chat', app=App(app_chat_ui, app_chat_server)),
]

app = Starlette(routes=routes)

USERNAME=os.environ["APP_USERNAME"]
PASSWORD=os.environ["APP_PASSWORD"]

app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend(USERNAME, PASSWORD))

