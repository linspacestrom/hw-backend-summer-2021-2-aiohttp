class AuthRequiredMixin:
    async def authorize(self):
        from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
        from aiohttp_session import get_session

        session = await get_session(self.request)
        admin_id = session.get("admin_id")
        if not admin_id:
            raise HTTPUnauthorized

        admin = await self.store.admins.get_by_id(int(admin_id))
        if admin is None:
            raise HTTPForbidden

        self.request.admin = admin
        return admin
