from discord.ext import commands
from commands.util import find_img, execute_command
import os, cv2, uuid, asyncio, discord

class GifCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.colours = []
        with open("scripts/data/magick_colours.txt", 'r') as f:
            for colour in f.readlines():
                self.colours.append(colour.lower().split("\n")[0])

    async def execute_gif_command(self, ctx, script, params="", input_dimensions=False, input_img=None):
        if input_img is None:
            in_file = await find_img(ctx)
            if in_file is None:
                return
        else:
            in_file = input_img

        try:
            height, width, _ = cv2.imread(in_file).shape
            if width > 800 or height > 800:
                if width > height:
                    code, _ = await execute_command(f"convert {in_file} -resize 800x {in_file}")
                    height  = int( height * (800/width) )
                    width   = 800
                else:
                    code, _ = await execute_command(f"convert {in_file} -resize x800 {in_file}")
                    width   = int( width * (800/height) )
                    height  = 800
                if code != 0:
                    await ctx.send(f"{ctx.author.mention} Something went wrong")
            uuid = in_file.split(".")[0]
            out_file = f"{uuid}.gif"
            command = f"bash scripts/{script}.sh {in_file} {out_file} "
            if input_dimensions:
                command += f"{width} {height} "
            command += params
            code, _ = await execute_command(command)
            if code == 0:
                await ctx.send(f"{ctx.author.mention}", file=discord.File(out_file))
            else:
                await ctx.send(f"{ctx.author.mention} Something went wrong")

        except Exception as e:
            print(e)
            await ctx.send(f"{ctx.author.mention} Gif too large, give me a moment to compress")
            try:
                await execute_command(f"convert {out_file} -fuzz 10% -layers Optimize {out_file}")
                await ctx.send(f"{ctx.author.mention}", file=discord.File(out_file))
            except:
                await ctx.send(f"{ctx.author.mention} Gif still too large after compression")
        finally:
            try:
                os.system(f"rm {in_file}")
                os.system(f"rm {out_file}")
            except:
                return

    @commands.command()
    async def mesmerisegif(self, context, colour1: str="black", colour2: str="white", img_file=None):
        if colour1 in self.colours:
            if colour2 in self.colours:
                await self.execute_gif_command(context, "mesmerize_helper", f"{colour1} {colour2}", input_img=img_file)
            else:
                await context.send(f"{context.author.mention} I don't recognise that colour")
        else:
             await contex.send(f"{context.author.mention} I don't recognise that colour")

    @commands.command()
    async def wigglegif(self, context, strength: int=25, wavelength: int=100, img_file=None):
        if (10 <= strength <= 100):
            if (10 <= wavelength <= 100):
                await self.execute_gif_command(context, "wiggle_helper", f"{wavelength} {strength}", input_img=img_file)
            else:
                await context.send(f"{context.author.mention} Wavelength must be between 10-100")
        else:
            await context.send(f"{context.author.mention} Strength must be between 10-100")

    @commands.command()
    async def blackholegif(self, context, img_file=None):
        await self.execute_gif_command(context, "black_hole", input_img=img_file)

    @commands.command()
    async def explodegif(self, context, img_file=None):
        await self.execute_gif_command(context, "explode_gif", input_img=img_file)

    @commands.command()
    async def implodegif(self, context, img_file=None):
        await self.execute_gif_command(context, "implode_gif", input_img=img_file)

    @commands.command()
    async def spinblurgif(self, context, img_file=None):
        await self.execute_gif_command(context, "spinblur_gif", input_img=img_file)

    @commands.command()
    async def huegif(self, context, img_file=None):
        await self.execute_gif_command(context, "hue_gif", input_img=img_file)

    @commands.command()
    async def distortgif(self, context, img_file=None):
        await self.execute_gif_command(context, "turbulence_gif", input_img=img_file)

    @commands.command()
    async def huetextgif(self, context, *params, img_file=None):
        text = ""
        for param in params:
            text += f" {param}"
        text = f'"{text[1:]}"'
        await self.execute_gif_command(context, "hue_text", f"{text}", input_dimensions=True, input_img=img_file)
