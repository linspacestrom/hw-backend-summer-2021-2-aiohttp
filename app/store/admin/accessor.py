import typing
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        cfg = app.config.admin
        admin = await self.get_by_email(cfg.email)
        if admin is None:
            await self.create_admin(cfg.email, cfg.password)

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def get_by_id(self, admin_id: int) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.id == admin_id:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        hashed = sha256(password.encode()).hexdigest()
        admin = Admin(
            id=len(self.app.database.admins) + 1, email=email, password=hashed
        )
        self.app.database.admins.append(admin)
        return admin

    async def check_password(self, admin: Admin, password: str) -> bool:
        return admin.password == sha256(password.encode()).hexdigest()
