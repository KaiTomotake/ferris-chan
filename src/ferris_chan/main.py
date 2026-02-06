import pathlib
import os
import enum
import datetime

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

class ModerateAction(enum.Enum):
    BAN = enum.auto()
    KICK = enum.auto()
    TIMEOUT = enum.auto()

class ModerateModal(discord.ui.Modal):
    def __init__(
            self, 
            act: ModerateAction, 
            target: discord.Member, 
            time: datetime.datetime | None = None
        ):
        super().__init__(title="ModeratePanel")
        self.act = act
        self.target = target
        self.time = time
        self.reason = discord.ui.TextInput(
            label="理由", 
            style=discord.TextStyle.long
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.act == ModerateAction.BAN:
            try:
                await self.target.ban(reason=self.reason.value)
            except Exception as e:
                await interaction.followup.send((f"`{e}`"))
                return
        elif self.act == ModerateAction.KICK:
            try:
                await self.target.kick(reason=self.reason.value)
            except Exception as e:
                await interaction.followup.send((f"`{e}`"))
                return                
        elif self.act == ModerateAction.TIMEOUT:
            try:
                await self.target.timeout(self.time, reason=self.reason.value)
            except Exception as e:
                await interaction.followup.send((f"`{e}`"))
                return 
        else:
            return
        embed = discord.Embed(title="Report")
        embed.add_field(name="対象", value=f"`{self.target.name}`")
        embed.add_field(name="実行者", value=f"`{interaction.user.name}`")
        embed.add_field(name="理由", value=self.reason.value)
        embed.add_field(
            name="時刻", 
            value=datetime.datetime.now().strftime("%d/%m/%y %H:%M")
        )
        await interaction.followup.send(embed=embed)

@discord.app_commands.command(name="ban", description="メンバーをBANします")
@discord.app_commands.default_permissions(ban_members=True)
@discord.app_commands.describe(target="BANする対象")
async def ban(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.send_modal(ModerateModal(ModerateAction.BAN, target))

@discord.app_commands.command(name="kick", description="メンバーをKICKします")
@discord.app_commands.default_permissions(kick_members=True)
@discord.app_commands.describe(target="KICKする対象")
async def kick(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.send_modal(ModerateModal(ModerateAction.KICK, target))

@discord.app_commands.command(name="timeout", description="メンバーをTIMEOUTします")
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.describe(target="TIMEOUTする対象", until="期間（日数）")
async def timeout(interaction: discord.Interaction, target: discord.Member, until: int):
    t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=until)
    await interaction.response.send_modal(ModerateModal(ModerateAction.TIMEOUT, target, t))

if __name__ == "__main__":
    dotenv.load_dotenv(pathlib.Path(__file__).parent.absolute().joinpath(".env"))
    client = Client()
    client.tree.add_command(ban)
    client.tree.add_command(kick)
    client.tree.add_command(timeout)
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
