from discord.ext import commands
from commands.util import find_url, download_img
import os

class UtilCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register2(self, context, type: str, name: str):
        if type == "overlay" or type == "eyes":
            type = "overlays" if type == "overlay" else "eyes"
            if context.guild is not None:
                guild = str(context.guild).replace(" ", "_")
                chan_messages = await context.channel.history(limit=50).flatten()
                url = find_url(context, chan_messages)
                if url is not None:
                    if not os.path.isdir(f"imageEffects/{guild}"):
                        os.system(f"mkdir imageEffects/{guild} imageEffects/{guild}/overlays imageEffects/{guild}/eyes")
                    if name not in [ file.split(".")[0] for file in os.listdir(f"imageEffects/{guild}/{type}/") ]:
                        file = await download_img(url)
                        if file is not None:
                            os.system(f"cp {file} imageEffects/{guild}/{type}/{name}.png")
                            os.system(f"rm {file}")
                            await context.send(f"{context.author.mention} Successfully registered new {type} command")
                        else:
                            await context.send(f"{context.author.mention} Something went wrong")
                    else:
                        await context.send(f"{context.author.mention} There is already an {type} command with that name, remove it with >remove {type} {name}")
                else:
                    await context.send(f"{context.author.mention} Could not find an image to use")
            else:
                await context.send(f"{context.author.mention} You can only use this feature in servers")
        else:
            await context.send(f"{context.author.mention} You can only register overlays or eyes")

    @commands.command()
    async def remove2(self, context, type: str, name: str):
        if type == "overlay" or type == "eyes":
            type = "overlays" if type == "overlay" else "eyes"
            if context.guild is not None:
                guild = str(context.guild).replace(" ", "_")
                for file in [ file for file in os.listdir(f"imageEffects/{guild}/{type}/") ]:
                    if name == file.split(".")[0]:
                        os.system(f"rm imageEffects/{guild}/{type}/{file}")
                        await context.send(f"{context.author.mention} Successfully removed {type} command")
                        break
                else:
                    await context.send(f"{context.author.mention} There is no registered {type} command with the name {name}")
            else:
                await context.send(f"{context.author.mention} You can only use this feature in servers")
        else:
            await context.send(f"{context.author.mention} You can only remove overlays or eyes")

    @commands.command()
    async def view(self, context, type: str):
        if type == "overlays" or type == "eyes":
            message = ""
            message += f"{context.author.mention} Global {type} commands:\n"
            for i, name in enumerate( [ file.split(".")[0] for file in os.listdir(f"imageEffects/all/{type}/") ] ):
                message += f"    ({i+1}) add {name}\n"
            if context.guild is not None:
                guild = str(context.guild).replace(" ", "_")
                if os.path.isdir(f"imageEffects/{guild}"):
                    commands = [ file.split(".")[0] for file in os.listdir(f"imageEffects/{guild}/{type}/") ]
                    if len(commands) > 0:
                        message += f"Custom {type} commands for this server:\n"
                        for i, command in enumerate(commands):
                            message += f"    ({i+1}) add {command}\n"
                    else:
                        message += f"There are currently no custom {type} commands for this server"
                else:
                    message += f"There are currently no custom {type} commands for this server"
            await context.send(message)
        else:
            await context.send(f"{context.author.mention} You can only view overlays or eyes")
