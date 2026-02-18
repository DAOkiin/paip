from __future__ import annotations

import asyncio
from dataclasses import dataclass

from aiogram import Bot


@dataclass
class NotificationAttempt:
    status: str
    error: str | None = None


class TelegramNotifier:
    def __init__(self, bot_token: str | None):
        self.bot_token = bot_token

    def send_message(self, chat_id: str, text: str) -> NotificationAttempt:
        if not self.bot_token:
            return NotificationAttempt(status="failed", error="TELEGRAM_BOT_TOKEN is not set")
        try:
            asyncio.run(self._send(chat_id, text))
        except Exception as exc:  # noqa: BLE001
            return NotificationAttempt(status="failed", error=str(exc))
        return NotificationAttempt(status="sent")

    async def _send(self, chat_id: str, text: str) -> None:
        bot = Bot(self.bot_token)
        try:
            await bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
        finally:
            await bot.session.close()
