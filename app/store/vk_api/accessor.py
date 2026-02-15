import typing
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession
from aiohttp.web_exceptions import HTTPInternalServerError

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"
API_HOST = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        if not app.config or not app.config.bot:
            return

        self.session = ClientSession()
        await self._get_long_poll_service()

        self.poller = Poller(store=app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller is not None:
            await self.poller.stop()
            self.poller = None

        if self.session is not None:
            await self.session.close()
            self.session = None

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        if not self.session or not self.app.config or not self.app.config.bot:
            return

        query = self._build_query(
            host=API_HOST,
            method="groups.getLongPollServer",
            params={
                "access_token": self.app.config.bot.token,
                "group_id": self.app.config.bot.group_id,
            },
        )
        async with self.session.get(query) as resp:
            data = await resp.json()
        response = data.get("response")
        if not response:
            raise HTTPInternalServerError()

        self.key = response["key"]
        self.server = response["server"]
        self.ts = int(response["ts"])

    async def poll(self):
        if not self.session or not self.server or not self.key or self.ts is None:
            return []

        params = {
            "act": "a_check",
            "key": self.key,
            "ts": self.ts,
            "wait": 25,
        }
        async with self.session.get(f"{self.server}?{urlencode(params)}") as resp:
            data = await resp.json()

        if "failed" in data:
            await self._get_long_poll_service()
            return []

        self.ts = int(data.get("ts", self.ts))
        raw_updates = data.get("updates", [])

        updates: list[Update] = []
        for u in raw_updates:
            try:
                if u.get("type") != "message_new":
                    continue
                msg = u["object"]["message"]
                updates.append(
                    Update(
                        type="message_new",
                        object=UpdateObject(
                            message=UpdateMessage(
                                id=int(msg["id"]),
                                from_id=int(msg["from_id"]),
                                text=str(msg.get("text", "")),
                            )
                        ),
                    )
                )
            except Exception:
                continue
        return updates

    async def send_message(self, message: Message) -> None:
        if not self.session or not self.app.config or not self.app.config.bot:
            return

        query = self._build_query(
            host=API_HOST,
            method="messages.send",
            params={
                "access_token": self.app.config.bot.token,
                "user_id": message.user_id,
                "random_id": 0,
                "message": message.text,
            },
        )
        async with self.session.get(query) as resp:
            await resp.read()
