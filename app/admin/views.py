from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import request_schema

from app.admin.schemes import AdminRequestSchema, AdminResponseSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminRequestSchema)
    async def post(self):
        admin = await self.store.admins.get_by_email(self.data["email"])
        if admin is None:
            raise HTTPForbidden

        ok = await self.store.admins.check_password(admin, self.data["password"])
        if not ok:
            raise HTTPForbidden

        from aiohttp_session import get_session

        session = await get_session(self.request)
        session["admin_id"] = admin.id

        return json_response(data=AdminResponseSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    async def get(self):
        admin = await self.authorize()
        return json_response(data=AdminResponseSchema().dump(admin))
