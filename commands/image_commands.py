from discord.ext   import commands
from commands.util import find_img, execute_command, combine_params
import os, cv2, math, uuid, random, asyncio, json, discord

class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.colours = []
        self.fonts = []
        with open("scripts/data/magick_colours.txt", 'r') as f:
            for colour in f.readlines():
                self.colours.append(colour.lower().split("\n")[0])
        with open("scripts/data/fonts.txt", 'r') as f:
            for font in f.readlines():
                self.fonts.append(font.lower().split("\n")[0])

    async def execute_magick_command(self, ctx, script, params="", ranges=[ (0, 100) ],
                                     force_png=False, resize=1800, input_dimensions=False,
                                     input_uuid=False, input_img=None):

        param_list = params.split(" ") if " " in params else [params]
        param_list = combine_params(param_list)
        mention = ctx.author.mention
        for i, param in enumerate(param_list):
            abs_val = param.replace(".","").replace("-","")
            if ranges[i] is None:
                continue
            if abs_val.isnumeric() and not ( ranges[i][0] <= float(param) <= ranges[i][1] ):
                error = f"value {i+1} must be between {ranges[i][0]} and {ranges[i][1]}"
                if input_img is None:
                    await ctx.send(f"{mention} {error}")
                return False, error
            elif ranges[i] == "colour" and param not in self.colours:
                error = f"value {i+1} must be a colour"
                if input_img is not None:
                    await ctx.send(f"{mention} {error}")
                return False, error

        if input_img is None:
            in_file = await find_img(ctx)
            if in_file is None:
                return
        else:
            in_file = input_img
        try:
            height, width, _ = cv2.imread(in_file).shape
            if width > resize or height > resize:
                if width > height:
                    code, _ = await execute_command(f"convert {in_file} -resize {resize}x {in_file}")
                    height = int( height * (resize/width) )
                    width  = resize
                else:
                    code, _ = await execute_command(f"convert {in_file} -resize x{resize} {in_file}")
                    width = int( width * (resize/height) )
                    height = resize
                if code != 0:
                    if input_img is None:
                        await ctx.send(f"{mention} Something went wrong")
                    else:
                        return False, "Something went wrong"
            uuid = in_file.split('.')[0]
            if force_png == True and ( in_file.endswith("jpeg") or in_file.endswith("jpg") ):
                out_file = f"{uuid}.png"
            else:
                out_file = in_file
            command = f"bash scripts/{script}.sh {in_file} {out_file} "
            if input_dimensions:
                command += f"{width} {height} "
            if input_uuid:
                command += f"{uuid} "
            command += params
            code, _ = await execute_command(command)
            if code == 0:
                if input_img is None:
                    await ctx.send( f"{mention}", file=discord.File(out_file) )
                else:
                    return True, out_file
            else:
                error = "Something went wrong"
                if input_img is None:
                    await ctx.send(f"{mention} {error}")
                else:
                    return False, error
        except Exception as e:
            print(e)
            await ctx.send(f"{mention} Output file was too large")
        finally:
            try:
                if input_img is None:
                    os.system(f"rm {in_file}")
                    if in_file != out_file:
                        os.system(f"rm {out_file}")
            except:
                return

    def search_for_file(self, type, name, guild):
        for file in os.listdir(f"imageEffects/{guild}/{type}/"):
            if name.lower() == file.split(".")[0].lower():
                return f"imageEffects/{guild}/{type}/{file}"
                break
        else:
            if guild != "all":
                for file in os.listdir(f"imageEffects/all/{type}/"):
                    if name.lower() == file.split(".")[0].lower():
                        return f"imageEffects/all/{type}/{file}"
                        break
                else:
                    return None
            else:
                return None

    async def legacy_command(self, context, type, img_file):
        if img_file is None:
            in_file = await find_img(context)
            if in_file is None:
                return
        else:
            in_file = img_file
        img = cv2.imread(in_file)
        cv2.imwrite( in_file, cv2.cvtColor(img, type) )
        if img_file is None:
            await context.send(f"{context.author.mention}", file=discord.File(in_file))
        else:
            return True, in_file

    @commands.command()
    async def trippy(self, context, img_file=None):
        return await self.legacy_command(context, cv2.COLOR_BGR2HSV, img_file)
    @commands.command()
    async def sonicoc(self, context, img_file=None):
        return await self.legacy_command(context, cv2.COLOR_BGR2XYZ, img_file)
    @commands.command()
    async def bend(self, context, strength: int=30, img_file=None):
        return await self.execute_magick_command(
            context, script="bend", params=str(strength), input_dimensions=True,
            force_png=True, input_img=img_file )
    @commands.command()
    async def wave(self, context, strength: int=25, img_file=None):
        return await self.execute_magick_command(
            context, script="wave", params=str(strength), input_dimensions=True,
            force_png=True, input_img=img_file )
    @commands.command()
    async def paint(self, context, strength: int=40, img_file=None):
        return await self.execute_magick_command(
            context, script="paint", params=str(strength), input_img=img_file )
    @commands.command()
    async def negate(self, context, colour: str="", img_file=None):
        ranges = ["colour"] if colour != "" else [None]
        return await self.execute_magick_command(
            context, script="negate", params=colour, input_img=img_file, ranges=ranges )
    @commands.command()
    async def duotone(self, context, colour1: str="yellow", colour2: str="red", img_file=None):
        return await self.execute_magick_command(
            context, script="swap_colours", params=f"{colour1} {colour2}", input_img=img_file,
            ranges=["colour", "colour"] )
    @commands.command()
    async def hue(self, context, strength: int=25, img_file=None):
        return await self.execute_magick_command(
            context, script="change_hue", params=str(strength), input_img=img_file )
    @commands.command()
    async def contrast(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="contrast", params=str(strength), input_img=img_file )
    @commands.command()
    async def charcoal(self, context, strength: int=30, img_file=None):
        return await self.execute_magick_command(
            context, script="charcoal", params=str(strength), input_img=img_file )
    @commands.command()
    async def cube(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="cube", force_png=True, input_img=img_file )
    @commands.command()
    async def edge(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="edge", params=str(strength), input_img=img_file )
    @commands.command()
    async def emboss(self, context, strength: int=35, img_file=None):
        return await self.execute_magick_command(
            context, script="emboss", params=str(strength), input_img=img_file )
    @commands.command()
    async def explode(self, context, strength: int=40, img_file=None):
        return await self.execute_magick_command(
            context, script="explode", params=str(strength), input_img=img_file )
    @commands.command()
    async def flipx(self, context, img_file=None):
        return await self.execute_magick_command( context, script="flipx", input_img=img_file )
    @commands.command()
    async def flipy(self, context, img_file=None):
        return await self.execute_magick_command( context, script="flipy", input_img=img_file )
    @commands.command()
    async def implode(self, context, strength: int=30, img_file=None):
        return await self.execute_magick_command(
            context, script="implode", params=str(strength), input_img=img_file )
    @commands.command()
    async def photo(self, context, *params, img_file=None):
        text = f""
        for i, param in enumerate(params):
            param.replace("!", "\!")
            text += param+" " if i < len(params)-1 else param
        if len(params) > 0:
            text = f'"{text}"'
        await self.execute_magick_command(
            context, script="photo", params=text, force_png=True )
    @commands.command()
    async def depress(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="make_sad", input_img=img_file )
    @commands.command()
    async def rotate(self, context, degrees: int=90, img_file=None):
        return await self.execute_magick_command(
            context, script="rotate", params=str(degrees), ranges=[ (-360,360) ],
            force_png=True)
    @commands.command()
    async def saturate(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="saturation", params=str(strength), input_img=img_file )
    @commands.command()
    async def sketch(self, context, strength: int=30, img_file=None):
        return await self.execute_magick_command(
            context, script="sketch", params=str(strength), input_img=img_file )
    @commands.command()
    async def solarise(self, context, strength: int=60, img_file=None):
        return await self.execute_magick_command(
            context, script="solarize", params=str(strength), input_img=img_file )
    @commands.command()
    async def swirl(self, context, strength: int=180, img_file=None):
        return await self.execute_magick_command(
            context, script="swirl", params=str(strength), ranges=[ (-720,720) ],
            input_img=img_file )
    @commands.command()
    async def blur(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="blur", params=str(strength), input_img=img_file )
    @commands.command()
    async def floortexture(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="floor_texture", input_img=img_file )
    @commands.command()
    async def motionblur(self, context, strength: int=50, angle: int=45, img_file=None):
        return await self.execute_magick_command(
            context, script="motion", params=f"{strength} {angle}",
            ranges=[ (0,100), (-360,360) ], resize=1200, input_img=img_file )
    @commands.command()
    async def spinblur(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="spin", params=str(strength), input_img=img_file )
    @commands.command()
    async def flood(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="flood", input_dimensions=True, input_img=img_file )
    @commands.command()
    async def isolatecolour(self, context, colour: str, img_file=None):
        return await self.execute_magick_command(
            context, script="isolatecolor_helper", params=colour, ranges=["colour"],
            input_img=img_file )
    @commands.command()
    async def putonmug(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="mug", input_img=img_file)
    @commands.command()
    async def reflect(self, context, r_type: str="left", x: int=50, img_file=None):
        if r_type.lower() not in ["left", "right", "blend"]:
            if img_file is None:
                await context.send(f"{context.author.mention} Type must be 'left', 'right', or 'blend'")
            else:
                return False, "Type must be 'left', 'right', or 'blend'"
        else:
            return await self.execute_magick_command(
                context, script="reflect_helper", params=f"{x} {r_type.lower()}",
                ranges=[(0,100), None], input_dimensions=True, input_img=img_file)
    @commands.command()
    async def sphere(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="sphere_helper", force_png=True, input_img=img_file)
    @commands.command()
    async def censor(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="censor", resize=1200, input_dimensions=True, input_img=img_file)
    @commands.command()
    async def stainedglass(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="stainedglass_helper", resize=1200, input_dimensions=True,
            input_img=img_file)
    @commands.command()
    async def hexagon(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="hexagon", resize=1200, input_dimensions=True, input_img=img_file)
    @commands.command()
    async def vintage(self, context, img_file=None):
        return await self.execute_magick_command(context, script="vintage", input_img=img_file)
    @commands.command()
    async def dmt(self, context, img_file=None):
        formula = random.choice( [1,2,6,8] )
        gain    = random.uniform(0.5, 3)
        return await self.execute_magick_command(
            context, script="dmt", params=f"{formula} {gain}", ranges=[None,None],
            resize=500, input_img=img_file)
    @commands.command()
    async def tear(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="tear", force_png=True, input_img=img_file)
    @commands.command()
    async def toon(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="toon_helper", input_img=img_file)
    @commands.command()
    async def watercolour(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="watercolor_helper", input_img=img_file)
    @commands.command()
    async def kaleidoscope(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="kaleidoscope_helper", input_img=img_file)
    @commands.command()
    async def puzzle(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="puzzle_helper", resize=1200, input_dimensions=True,
            force_png=True, input_img=img_file)
    @commands.command()
    async def zoomblur(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="zoomblur", params=str(strength), resize=1200,
            input_img=img_file)
    @commands.command()
    async def cellshade(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="cartoon", resize=800, input_img=img_file)
    @commands.command()
    async def glass(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="glasseffects", resize=1200, input_img=img_file)
    @commands.command()
    async def crt(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="crtscreen", input_img=img_file)
    @commands.command()
    async def crosshatch(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="crosshatch_helper", params=str(strength), resize=1200,
            input_img=img_file)
    @commands.command()
    async def ripple(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="ripple_helper", params=str(strength), resize=1200,
            input_img=img_file)
    @commands.command()
    async def distort(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="distortion", params=str(strength), input_img=img_file)
    @commands.command()
    async def deepfry(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="deepfry", params=str(strength), input_img=img_file)
    @commands.command()
    async def vignette(self, context, colour: str="black", img_file=None):
        return await self.execute_magick_command(
            context, script="vignette_helper", params=colour, ranges=["colour"],
            input_img=img_file)
    @commands.command()
    async def nightvision(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="nightvision", input_img=img_file)
    @commands.command()
    async def freeze(self, context, strength: int=50, img_file=None):
        return await self.execute_magick_command(
            context, script="frosted_helper", params=str(strength), input_img=img_file)
    @commands.command()
    async def planet(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="planet_helper", input_dimensions=True,
            input_img=img_file)
    @commands.command()
    async def recursion(self, context, rotation: int=0, img_file=None):
        angle = random.randint(-180, 180)
        return await self.execute_magick_command(
            context, script="recursion_helper", params=f"{angle} {rotation}",
            ranges=[(-180,180), (0,180)], resize=1200, input_img=img_file)
    @commands.command()
    async def oldpicture(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="oldpicture", resize=1200, input_img=img_file)
    @commands.command()
    async def mandala(self, context, img_file=None):
        n = random.randint(6,  12)
        r = random.randint(0, 360)
        t = random.randint(0, 200)
        return await self.execute_magick_command(
            context, script="mandalascope_helper", params=f"{n} {r} {t}",
            ranges=[(6,12), (0,360), (0, 200)], resize=800, input_img=img_file)
    @commands.command()
    async def collage(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="collage", resize=800, input_img=img_file)
    @commands.command()
    async def putonshirt(self, context, img_file=None):
        return await self.execute_magick_command(
            context, script="tshirt_helper", input_img=img_file)
    @commands.command()
    async def xpcollage(self, context, name: str="image", img_file=None):
        if img_file is None:
            in_file = await find_img(context)
            if in_file is None:
                return
        else:
            in_file = img_file
        try:
            height, width, _ = cv2.imread(in_file).shape
            if width > 800 or height > 800:
                if width > height:
                    code, _ = await execute_command(f"convert {in_file} -resize 800x {in_file}")
                    height = int( height * (800/width) )
                    width  = 800
                else:
                    code, _ = await execute_command(f"convert {in_file} -resize x800 {in_file}")
                    width  = int( width * (800/height) )
                    height = 800
            file_type = in_file.split(".")[1]
            code, _  = await execute_command(f"bash scripts/xpcollage.sh {in_file} upload/{name}.{file_type} {width} {height}")
            out_file = f"upload/{name}_montage.{file_type}"
            if code == 0:
                if img_file is None:
                    await context.send( f"{context.author.mention}", file=discord.File(out_file) )
                else:
                    return True, out_file
            else:
                error = "Something went wrong"
                if img_file is None:
                    await context.send(f"{context.author.mention} {error}")
                else:
                    return False, error
        except Exception as e:
            await context.send(f"{context.author.mention} Output file was too large")
        finally:
            try:
                if img_file is None:
                    os.system(f"rm {in_file}")
                    if in_file != out_file:
                        os.system(f"rm {out_file}")
            except:
                return
    async def text_helper(self, context, params, location, img_file):
        stroke, fill, font = "black", "white", "Helvetica-Bold"
        warnings = ""
        text = f'"{params[0]}"'
        if len(params) != 1:
            params = params[1:]
            if  len(params) % 2 == 0 and len(params) <= 6:
                for param_type, param_val in zip(params[::2], params[1::2]):
                    if param_type.lower() == "stroke":
                        if param_val.lower() in self.colours:
                            stroke = param_val
                        else:
                            warnings += ", I don't recognise that stroke colour - using default,"
                    elif param_type.lower() == "fill":
                        if param_val.lower() in self.colours:
                            fill = param_val
                        else:
                            warnings += ", I don't recognise that fill colour - using default,"
                    elif param_type.lower() == "font":
                        if param_val.lower() in self.fonts:
                            font = param_val
                        else:
                            warnings += ", I don't recognise that font - using default,"
                    else:
                        warnings += f", {param_type} is not a valid input,"
            else:
                return False, "Command should be of the form (brackets are optional) >*position*text \"*your text*\" (fill *colour*) (stroke *colour*) (font *font*)"

        if img_file is None and warnings != "":
            await context.send(f"{context.author.mention} {warnings}")
        comm_response = await self.execute_magick_command(
            context, script="text", params=f"{location} {text} {fill} {stroke} {font}",
            input_dimensions=True, input_uuid=True, input_img=img_file,
            ranges=[None,None,None,None,None] )
        if img_file is not None:
            success, response = comm_response
            return success, response + warnings
    @commands.command()
    async def toptext(self, context, *params, img_file=None):
        return await self.text_helper(context, params, "North", img_file)
    @commands.command()
    async def bottomtext(self, context, *params, img_file=None):
        return await self.text_helper(context, params, "South", img_file)
    @commands.command()
    async def middletext(self, context, *params, img_file=None):
        return await self.text_helper(context, params, "Center", img_file)
    @commands.command()
    async def add(self, context, name: str, img_file=None):
        guild = str(context.guild).replace(" ", "_") if context.guild is not None else "all"
        file  = self.search_for_file("overlays", name, guild)
        if file is not None:
            return await self.execute_magick_command(
                context, script="overlay", params=file, input_dimensions=True, input_img=img_file )
        else:
            await context.send(f"{context.author.mention} Could not find overlay with the name {name}")
    @commands.command()
    async def apply(self, context, *params, img_file=None):
        valid_types = ["cat", "human", "both"]
        type  = "human"
        scale = None
        if len(params) == 2 and params[1] == "eyes":
            name  = params[0]
            part  = params[1]
        elif len(params) == 3:
            if params[2].replace(".","").isnumeric() and params[1] == "eyes":
                name  = params[0].lower()
                scale = float(params[2])
            elif params[2]  == "eyes" and params[0] in valid_types:
                type = params[0]
                name = params[1].lower()
            else:
                await context.send(f"{context.author.mention} Command must be of the form ->apply (cat/human/both) *name* eyes (scale) - bracket parts are optional")
                return
        elif len(params) == 4 and params[0] in valid_types and params[2] == "eyes" and params[3].replace(".","").isnumeric():
            type = params[0]
            name = params[1].lower()
            scale = float(params[3])
        else:
            await context.send(f"{context.author.mention} Command must be of the form ->apply (cat/human/both) *name* eyes (scale) - bracket parts are optional")

        if img_file is None:
            in_file = await find_img(context)
            if in_file is None:
                return
        else:
            in_file = img_file

        guild = str(context.guild).replace(" ", "_") if context.guild is not None else "all"
        eye_file = self.search_for_file("eyes", name, guild)
        if eye_file is not None:
            code, out = await execute_command(f"python3 scripts/face_detector.py {in_file} {type}")
            if code == 0:
                if out != "Don't recognise type":
                    str_landmarks = out.strip("[]")
                    str_landmarks = str_landmarks.replace("'", "\"").replace("(", "[").replace(")","]").replace("\n","")
                    str_landmarks = str_landmarks.replace("}]", "}").split("}, ")
                    if str_landmarks[0] != "":
                        send = True if img_file is None else False
                        return await self.eye_command(
                            context, str_landmarks, in_file, eye_file, scale, send )
                    else:
                        await context.send(f"{context.author.mention} Couldn't detect any faces, if the image contains a cat, try using >apply cat *name* eyes (scale)")
                else:
                    await context.send(f"{context.author.mention} Can only specify human or cat types")
            else:
                await context.send(f"{context.author.mention} Something went wrong")
        else:
            await context.send(f"{context.author.mention} Could not find overlay with the name {name}")

    async def eye_command(self, context, str_landmarks, in_file, eye_file, scale, send):
        success = False
        for landmark in str_landmarks:
            if not landmark.endswith("}}"):
                landmark += "}"
            js_landmarks = json.loads(landmark)
            type = js_landmarks["type"]
            landmarks = js_landmarks["landmarks"]
            if type == "human":
                totalLX, totalLY = 0, 0
                totalRX, totalRY = 0, 0
                for lPoint, rPoint in zip(landmarks["left_eye"], landmarks["right_eye"]):
                    totalLX += lPoint[0]
                    totalLY += lPoint[1]
                    totalRX += rPoint[0]
                    totalRY += rPoint[1]
                lEye_center = int( totalLX / len(landmarks["left_eye"]) ), int( totalLY / len(landmarks["left_eye"]) )
                rEye_center = int( totalRX / len(landmarks["right_eye"]) ), int( totalRY / len(landmarks["right_eye"]) )

                face_width = abs( landmarks["right_cheek"][0] - landmarks["left_cheek"][0] )
                lEye_width = abs( landmarks["left_eye"][0][0] - landmarks["left_eye"][2][0] )
                rEye_width = abs( landmarks["right_eye"][0][0] - landmarks["right_eye"][2][0] )
                eye_width  = max(lEye_width, rEye_width)
            elif type == "cat":
                lEye_center, rEye_center = landmarks["left_eye"], landmarks["right_eye"]
                face_width = abs( landmarks["right_right_ear"][0] - landmarks["left_left_ear"][0] )
                eye_width  = int(face_width * 0.3)

            xDiff = lEye_center[0] - rEye_center[0]
            yDiff = rEye_center[1] - lEye_center[1]
            angle = math.degrees( math.atan(yDiff/xDiff) )
            if eye_file.split("/")[-1][:-4] == "power":
                new_img_width = int(face_width*1.2)
                new_img_width *= scale if scale is not None else 1
            else:
                new_img_width = eye_width
                new_img_width *= scale if scale is not None else 1

            uuid = in_file.split("/")[-1][:-4]
            prepared_eye_img = f"upload/prep_eye_{uuid}.png"
            code, _ = await execute_command(
                f"convert {eye_file} -resize {new_img_width}x -alpha set -background none -rotate {-angle} {prepared_eye_img}" )
            if code != 0:
                continue

            eye_img_h, eye_img_w, _ = cv2.imread(prepared_eye_img).shape
            x1, y1 = lEye_center[0]-int(eye_img_w/2), lEye_center[1]-int(eye_img_h/2)
            x2, y2 = rEye_center[0]-int(eye_img_w/2), rEye_center[1]-int(eye_img_h/2)
            code, _ = await execute_command(
                f"bash scripts/apply_eyes.sh {in_file} {in_file} {prepared_eye_img} \
                {x1} {y1} {x2} {y2}")
            if code == 0:
                success = True
            else:
                continue

        os.system(f"rm {prepared_eye_img}")
        if success:
            if send:
                await context.send(f"{context.author.mention}", file=discord.File(in_file))
                os.system(f"rm {in_file}")
            else:
                return True, in_file
        else:
            if send:
                await context.send(f"{context.author.mention} Something went wrong")
            else:
                return False, "Something went wrong"
