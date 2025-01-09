from starlette.authentication import AuthenticationBackend, SimpleUser, AuthCredentials
import base64
from starlette.requests import Request


class BasicAuthBackend(AuthenticationBackend):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def authenticate(self, request: Request):
        # Extract the Authorization header
        auth = request.headers.get("Authorization")
        if auth:
            scheme, credentials = auth.split()
            if scheme.lower() == "basic":
                # Correct base64 decoding for Python 3
                decoded = base64.b64decode(credentials).decode("utf-8")
                user, password = decoded.split(":")
                if user == self.username and password == self.password:
                    return AuthCredentials(["authenticated"]), SimpleUser(user)
        return None