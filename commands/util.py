import asyncio, subprocess, aiohttp, aiofiles, uuid

async def execute_command(command):
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode()

def find_url(ctx, chan_messages):
    if len(ctx.message.attachments) > 0:
        url = ctx.message.attachments[0].url
        if not (url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".png")):
            return None
        else:
            return ctx.message.attachments[0].url
    else:
        for message in chan_messages:
            if len(message.attachments) > 0:
                url = message.attachments[0].url
                if not (url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".png")):
                    continue
                else:
                    return url
        return None

async def download_img(url):
    HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                type, format = response.headers["Content-Type"].split('/')
                if type == "image":
                    file_name = f"upload/{uuid.uuid4()}.{format}"
                    img_file = await aiofiles.open(file_name, mode="wb")
                    await img_file.write( await response.read() )
                    await img_file.close()
                    return file_name
                else:
                    return None
            else:
                return None

async def find_img(ctx):
    chan_messages = await ctx.channel.history(limit=50).flatten()
    url = find_url(ctx, chan_messages)
    if url is not None:
        img_file = await download_img(url)
        if img_file is not None:
            return img_file
        else:
            await ctx.send(f"{ctx.author.mention} Could not download image")
            return None
    else:
        await ctx.send(f"{ctx.author.mention} Could not find an image to edit")
        return None

def combine_params(params):
    start_index = 0
    combined_param = ""
    combined_list  = []
    quote_positions = [ i for i, param in enumerate(params) if "\"" in param ]
    if len(quote_positions) != 2:
        return params
    else:
        for i in range(quote_positions[0], quote_positions[1]+1):
            combined_param += f"{params[i]} "
        if quote_positions[0] > 0:
            combined_list = params[:quote_positions[0]] + [combined_param[1:-2]]
        else:
            combined_list = [combined_param[1:-2]]
        if quote_positions[1] < len(params)-1:
            combined_list += params[quote_positions[1]+1:]
        return combined_list
    """
    for i, param in enumerate(params):
        if param.startswith("\""):
            start_index = i
            print("param starts with \"")
            for i, param in enumerate(params):
                combined_param += f"{param} "
                if param.endswith("\""):
                    print("found close \"")
                    params = params[i+1:]
                    break
            else:
                return params
        print(f"inserting {combined_param} to start of {params}")
        return [combined_param[1:-2]] + params
    return params
    """
