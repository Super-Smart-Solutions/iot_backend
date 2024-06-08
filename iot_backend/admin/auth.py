from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request


class AdminAuth(AuthenticationBackend):
    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == "admin@example.com" and password == "super_user@159":
            request.session.update({"token": "testtoken"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


authentication_backend = AdminAuth(secret_key="shljdvgHWRHEJGVHJRBGWERbfgB;KWR")
