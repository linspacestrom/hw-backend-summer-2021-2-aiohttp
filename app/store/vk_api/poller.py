import asyncio
from asyncio import Task

from app.store import Store


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    async def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self) -> None:
        self.is_running = False
        if self.poll_task is None:
            return
        await self.poll_task
        self.poll_task = None

    async def poll(self) -> None:
        while self.is_running:
            try:
                updates = await self.store.vk_api.poll()
                if updates:
                    await self.store.bots_manager.handle_updates(updates=updates)
            except Exception:
                await asyncio.sleep(1)
