from discord.ext   import commands
from commands.util import download_img, execute_command
import asyncio, aiohttp, aiofiles, uuid, cv2, random, discord, os, wikipediaapi

class SearchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def search_local(self, ctx, query, type="image", send=True):
        file_type = ".jpg" if type == "image" else ".mp4"
        files = [ f"{query}/{file}" for file in os.listdir(f"{query}/") if file.endswith(file_type) ]
        choice = random.choice(files)
        new_name = f"upload/{uuid.uuid4()}{file_type}"
        os.system(f"cp {choice} {new_name}")
        if send:
            await ctx.send( f"{ctx.author.mention}", file=discord.File(new_name) )
            os.system(f"rm {new_name}")
        else:
            if type == "image":
                return True, new_name
            else:
                os.system(f"rm {new_name}")
                return False, "You can only chain commands with images, not videos"

    async def search_online(self, ctx, query, type="image", send=True):
        query = query.replace("; ", " AND ")
        query = query.replace(';', " AND ")
        HEADERS = { "Authorization" : "Client-ID TOKEN" }
        max_page = 100
        searching_max_page = True
        while searching_max_page: #Try the find the amount of pages of results
            url = f"https://api.imgur.com/3/gallery/search/{max_page}?q_all={query}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=HEADERS) as response:
                    data = await response.json()
                    if data["status"] != 200 or len( data["data"] ) == 0:
                        max_page -= 10
                        if max_page < 0:
                            error = "Could not find any results"
                            if send:
                                await ctx.send(f"{ctx.author.mention} {error}")
                            return False, error
                    else:
                        searching_max_page = False

        page_choice = random.randint(0, max_page)
        url = f"https://api.imgur.com/3/gallery/search/{page_choice}?q_all={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                data = await response.json()
                if data["status"] == 200:
                    img_list = []
                    for gallery in data["data"]:
                        gallery_title = gallery["title"]
                        if not gallery["is_album"]:
                            if type == "image":
                                if gallery["type"].startswith(type) and not \
                                ( gallery["type"].endswith("gif") or gallery["type"].endswith("gifv") ):
                                    img_list.append( {"link":gallery["link"], "title":gallery_title} )
                            else:
                                if gallery["type"].startswith(type) or gallery["type"].endswith("gif") \
                                or gallery["type"].endswith("gifv"):
                                    img_list.append( {"link":gallery["link"], "title":gallery_title}  )
                        else:
                            for img in gallery["images"]:
                                if type == "image":
                                    if img["type"].startswith(type) and not \
                                    (img["type"].endswith("gif") or img["type"].endswith("gifv")):
                                        img_list.append( {"link":img["link"], "title":gallery_title}  )
                                else:
                                    if img["type"].startswith(type) or img["type"].endswith("gif") \
                                    or img["type"].endswith("gifv"):
                                        img_list.append( {"link":img["link"], "title":gallery_title}  )
                else:
                    error = f"Something went wrong"
                    if send:
                        await ctx.send(f"{ctx.author.mention} {error}")
                    return False, error
        img_choice = random.choice(img_list)
        link  = img_choice["link"]
        title = f"\n\"{img_choice['title']}\"" if img_choice['title'] is not None else ""
        if type == "image":
            file = await download_img(link)
            if send:
                await ctx.send( f"{ctx.author.mention}{title}", file=discord.File(file) )
                os.system(f"rm {file}")
            return True, file
        else:
            if send:
                await ctx.send( f"{ctx.author.mention}{title}\n{link}")
            else:
                return False, "You can only chain commands with images, not videos"

    def params_to_string(self, *params):
        query = ""
        for param in params:
            query += f"{param} "
        if query.lower().startswith("-v"):
            type  = "video"
            query = query[2:]
        else:
            type = "image"
        return type, query.strip()

    @commands.command()
    async def give(self, context, *params, send=True):
        type, query = self.params_to_string(*params)
        if query.lower() == "molly" or query.lower() == "mini" or query.lower() == "piupiu":
            return await self.search_local(context, query, type=type, send=send)
        else:
            return await self.search_online(context, query, type=type, send=send)

    @commands.command()
    async def giveinfo(self, context, *params):
        query = self.params_to_string(*params)
        wiki  = wikipediaapi.Wikipedia("en")
        page  = wiki.page(query)
        if page.exists():
            embed = discord.Embed(title=page.title, description=page.summary,
                color=0xff0000)
            embed.set_footer(text=page.fullurl)
            await context.send(f"{context.author.mention}", embed=embed)
        else:
            await context.send(f"{context.author.mention} Could not find any results")


    @commands.command()
    async def big(self, context, emoji: discord.Emoji, send=True):
        file = await download_img(f"https://cdn.discordapp.com/emojis/{emoji.id}.png")
        im_height, _, _ = cv2.imread(file).shape
        code, _ = await execute_command(f"bash scripts/resize.sh {file} {file} {int(im_height*1.5)} {int(im_height*1.5)}")
        if code == 0:
            if send:
                await context.send( f"{context.author.mention}", file=discord.File(file) )
                os.system(f"rm {file}")
            else:
                return True, file
        else:
            if send:
                await context.send(f"{context.author.mention} Something went wrong")
            else:
                return True, file

    @commands.command()
    async def givethumbnail(self, context, yt_id: str="UCmLiSrat4HW2k07ahKEJo4w", send=True):
        KEY = "TOKEN"
        channel_url = f"https://www.googleapis.com/youtube/v3/channels?key={KEY}&id={yt_id}&part=contentDetails"
        async with aiohttp.ClientSession() as session:
            async with session.get(channel_url) as response:
                data = await response.json()
                if response.status == 200:
                    if data["pageInfo"]["totalResults"] != 0:
                        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                    else:
                        error = "Could not find any channels matching that id"
                        if send:
                            await context.send(f"{context.author.mention} {error}")
                        return False, error
                else:
                    error = "Something went wrong"
                    if send:
                        await context.send(f"{context.author.mention} {error}")
                    return False, error
        playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems?key={KEY}&playlistId={uploads_id}&part=snippet&maxResults=50"
        thumbnails = []
        next_page  = None
        url = playlist_url
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        try:
                            next_page = data["nextPageToken"]
                        except KeyError:
                            next_page = None
                        for upload in data["items"]:
                            thumbnail_list = upload["snippet"]["thumbnails"]
                            if "maxres" in thumbnail_list:
                                thumbnails.append( thumbnail_list["maxres"]["url"] )
                            elif "high" in thumbnail_list:
                                thumbnails.append( thumbnail_list["high"]["url"] )
                            else:
                                continue

                        if next_page is None:
                            break
                        else:
                            url = playlist_url + f"&pageToken={next_page}"
                    else:
                        break
        choice = random.choice(thumbnails)
        file = await download_img(choice)
        if send:
            await context.send(f"{context.author.mention}", file=discord.File(file))
            os.system(f"rm {file}")
        else:
            return True, file
