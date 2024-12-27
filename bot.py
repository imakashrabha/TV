from aiohttp import web
from database.database import full_adminbase
from plugins import web_server
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyromod import listen
from datetime import datetime
import sys

from config import (
    ADMINS, API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, CHANNEL_ID, PORT, OWNER_ID
)

# Fix for current Pyrogram
from pyrogram import utils

def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"

utils.get_peer_type = get_peer_type_new


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Handle Force Sub Channel 1
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning("Bot can't export invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(
                    f"Please double-check the FORCE_SUB_CHANNEL value and ensure the bot is an admin "
                    f"in the channel with invite permissions. Current FORCE_SUB_CHANNEL: {FORCE_SUB_CHANNEL}"
                )

        # Handle Force Sub Channel 2
        if FORCE_SUB_CHANNEL2:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL2)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                self.invitelink2 = link
            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning("Bot can't export invite link from Force Sub Channel 2!")
                self.LOGGER(__name__).warning(
                    f"Please double-check the FORCE_SUB_CHANNEL2 value and ensure the bot is an admin "
                    f"in the channel with invite permissions. Current FORCE_SUB_CHANNEL2: {FORCE_SUB_CHANNEL2}"
                )

        # Handle DB Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test_message = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test_message.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make sure the bot is an admin in the DB Channel and double-check the CHANNEL_ID value. "
                f"Current CHANNEL_ID: {CHANNEL_ID}"
            )

        self.LOGGER(__name__).info(f"Bot @{usr_bot_me.username} started successfully!")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped gracefully.")

# Initialize and Run Bot
if __name__ == "__main__":
    try:
        bot = Bot()
        web_server.setup_routes(web.Application())
        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)
