from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)

from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_apispec import setup_aiohttp_apispec

from app.admin.models import Admin
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database = Database()


class Request(AiohttpRequest):
    admin: Admin | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    if app.config and app.config.session:
        import base64
        import hashlib

        try:
            key = base64.b64decode(app.config.session.key)
        except Exception:
            key = app.config.session.key.encode()

        if len(key) != 32:
            key = hashlib.sha256(key).digest()

        setup_session(app, EncryptedCookieStorage(key))
    setup_aiohttp_apispec(app, title="hw", version="1.0", url="/api/docs/swagger.json")
    setup_routes(app)
    setup_middlewares(app)
    setup_store(app)
    return app
