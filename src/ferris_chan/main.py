import pathlib
import os

import discord
import dotenv


class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.none()
        super().__init__(
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.playing, name="Rust言語"
            ),
        )
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


if __name__ == "__main__":
    dotenv.load_dotenv(pathlib.Path(__file__).parent.absolute().joinpath(".env"))
    client = Client()
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
