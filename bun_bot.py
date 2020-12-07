import discord, os, random
from discord.ext import commands
from commands.image_commands  import ImageCommands
from commands.search_commands import SearchCommands
from commands.util_commands   import UtilCommands
from commands.help_commands   import HelpCommands
from commands.gif_commands    import GifCommands
from commands.util import find_url, download_img, combine_params, execute_command

if __name__ == "__main__":
    KEY     = "NzcwNzM3OTc0NTE3ODI1NTY4.X5h7rA.eZdDxVhKjvCGFwKi1ZejW97YFrA"
    ask_responses = [
        "It is certain", "Without a doubt", "You may rely on it", "Yes definitely", "It is decidedly so",
         "As I see it, yes", "Most likely", "Yes", "Obviously", "That question was so stupid I'm not even responding",
         "Signs point to yes", "Better not tell you now", "Ask again later", "Cannot predict now",
         "Concentrate and ask again", "Don’t count on it", "Outlook not so good", "My sources say no",
         "Very doubtful", "My reply is no" ]

    bun_bot = commands.Bot(command_prefix="", case_insensitive=True, help_command=None)
    bun_bot.add_cog( ImageCommands(bun_bot)  )
    bun_bot.add_cog( SearchCommands(bun_bot) )
    bun_bot.add_cog( UtilCommands(bun_bot)   )
    bun_bot.add_cog( HelpCommands(bun_bot)   )
    bun_bot.add_cog( GifCommands(bun_bot)    )

    @bun_bot.event
    async def on_ready():
        print(f"Logged in, username: {bun_bot.user.name}, userID: {bun_bot.user.id}")

    @bun_bot.command()
    async def test(context):
        await context.send("response")

    @bun_bot.command()
    async def askbunny(context, *, question=""):
        if question == "":
            await context.send(f"{context.author.mention} You didn't event ask anything.")
        else:
            response = random.choice(ask_responses)
            await context.send(f"{context.author.mention} {response}")

    @bun_bot.command()
    async def chaingif(context, *, args):
        if "," not in args:
            return
        gif_params = args.split(",")[0]
        loop  = 0
        delay = 100
        if " " in gif_params.strip():
            final_param = None
            for gif_param in gif_params.split(" "):
                if gif_param.lower() == "-noloop":
                    loop = 1
                    final_param = "-noloop"
                elif gif_param.lower().startswith("-delay"):
                    try:
                        delay = int( gif_param[6:] )
                        final_param = f"-delay{delay}"
                        if not (1 <= delay <= 1000):
                            await context.send(f"{context.author.mention} Delay must be between 1 and 1000")
                            return
                    except:
                        await context.send(f"{context.author.mention} Delay must be a whole number")
                        return
            if final_param is not None:
                first_command = gif_params[ gif_params.index(final_param) + len(final_param) : ]
            else:
                first_command = gif_params
            args = first_command + args[ args.index(","): ]
        success, id, error = await chain(context, args=args, gif=True)
        if success:
            await execute_command(f"mogrify -resize 800x800\! -interlace Plane -gaussian-blur 0.05 -quality 50% upload/gif/{id}_gif*.*")
            with open(f"upload/gif/{id}.txt", 'w') as f:
                for file in sorted( [ "upload/gif/"+file for file in os.listdir("upload/gif/") if file.startswith(id) ] ):
                    f.write(f"{file}\n")
            await execute_command(f"convert -delay {delay} -loop {loop} @upload/gif/{id}.txt upload/{id}.gif")
            try:
                await context.send(f"{context.author.mention} {error}", file=discord.File(f"upload/{id}.gif"))
            except:
                await context.send(f"{context.author.mention} Output file too large, give me a moment to compress")
                await execute_command(f"convert upload/{id}.gif -fuzz 10% -layers Optimize upload/{id}.gif")
                try:
                    await context.send(f"{context.author.mention} {error}", file=discord.File(f"upload/{id}.gif"))
                except:
                    await context.send(f"{context.author.mention} Output file still too large")
            finally:
                os.system(f"rm upload/{id}.gif upload/gif/{id}_gif*.* upload/gif/{id}.txt")
        else:
            await context.send(f"{context.author.mention} {error[1:-1]}")

    @bun_bot.command()
    async def chain(context, *, args, gif=False):
        util_cog   = bun_bot.get_cog("UtilCommands")
        search_cog = bun_bot.get_cog("SearchCommands")
        image_cog  = bun_bot.get_cog("ImageCommands")
        gif_cog    = bun_bot.get_cog("GifCommands")
        util_commands   = util_cog.get_commands()
        search_commands = search_cog.get_commands()
        image_commands  = image_cog.get_commands()
        gif_commands    = gif_cog.get_commands()
        util_names   = [command.name for command in util_commands  ]
        search_names = [command.name for command in search_commands]
        image_names  = [command.name for command in image_commands ]
        gif_names    = [command.name for command in gif_commands   ]
        expensive_commands = ["dmt", "apply", "cellshade"]
        used_expensive = False
        error_message = ""
        send_file     = False

        commands = args.split(",")
        if len(commands) > 10:
            await context.send(f"{context.author.mention} You cannot chain more than 10 commands")
            return
        first_command = commands[0].strip().split(" ")
        first_name    = first_command[0].lower()
        first_args    = combine_params(first_command[1:]) if len(first_command) > 1 else []
        command_num   = 0
        if first_name in util_names:
            command_num   += 1
            error_message += " Error in command 1 - cannot chain utility commands,"
        elif first_name in gif_names:
            command_num   += 1
            error_message += " Error in command 1 - can only end chains with a gif command,"
        elif first_name in search_names:
            for search_command in search_commands:
                if first_name == search_command.name:
                    if first_name == "big":
                        if len(first_args) == 1 and ":" in first_args[0]:
                            emoji_id = first_args[0].split(":")[2][:-1]
                            for emoji in context.guild.emojis:
                                if emoji.id == int(emoji_id):
                                    first_args[0] = emoji
                    elif first_name == "giveinfo":
                        await context.send(f"{context.author.mention} Cannot chain the first command")
                        return
                    success, code = await search_command.__call__(context, *first_args, send=False)
                    if success:
                        img = code
                        if gif:
                            name, file_type = img[7:].split(".")
                            os.system(f"cp {img} upload/gif/{name}_gif{command_num}.{file_type}")
                        send_file = True
                        commands = commands[1:]
                        command_num += 1
                        break
                    else:
                        await context.send(f"{context.author.mention} {code}")
                        return
        else:
            chan_messages = await context.channel.history(limit=50).flatten()
            url = find_url(context, chan_messages)
            if url is not None:
                img = await download_img(url)
                if gif:
                    name, file_type = img[7:].split(".")
                    os.system(f"cp {img} upload/gif/{name}_gif{command_num}.{file_type}")
                if img is None:
                    await context.send(f"{context.author.mention} Could not download image")
                    return
            else:
                await context.send(f"{mention.author.mention} Could not find an image to edit")
                return

        for i, command in enumerate(commands):
            command_num  += 1
            command_split = command.strip().split(" ")
            command_name  = command_split[0].lower()
            command_args  = combine_params(command_split[1:]) if len(command_split) > 1 else []
            if command_name in util_commands:
                error_message += f" Error in command {command_num} - cannot chain utility commands,"
            elif command_name in search_names:
                error_message += f" Error in command {command_num} - can only start chain with search commands,"
            elif command_name in gif_names:
                if i != len(commands)-1:
                    error_message += f" Error in command {command_num} - can only end chains with a gif command,"
                elif not gif:
                    for gif_command in gif_commands:
                        if command_name == gif_command.name:
                            try:
                                if error_message != "":
                                    await context.send(f"{context.author.mention} {error_message[1:-1]}")
                                await gif_command.__call__(context, *command_args, img_file=img)
                                return
                            except Exception as e:
                                error_message += " Something went wrong in final gif command,"
                else:
                    error_message += " Cannot end gif chain with a gif command,"
            else:
                for image_command in image_commands:
                    if command_name == image_command.name:
                        try:
                            if command_name in expensive_commands:
                                if not used_expensive:
                                    success, code = await image_command.__call__(context, *command_args, img_file=img)
                                    used_expensive = True
                                else:
                                    error_message += f" Error in command {command_num} - Can only use expensive commands once in a chain,"
                                    continue
                            else:
                                success, code = await image_command.__call__(context, *command_args, img_file=img)
                            if not success:
                                error_message += f" Error in command {command_num} - {code}"
                            else:
                                if "," in code:
                                    error_message += code[code.index(",")+1:]
                                    img = code.split(",")[0]
                                else:
                                    img = code
                                if gif:
                                    name, file_type = img[7:].split(".")
                                    os.system(f"cp {img} upload/gif/{name}_gif{command_num}.{file_type}")
                                send_file = True
                        except Exception as e:
                            print(e)
                            error_message += f" Error in command {command_num} - Something went wrong,"
        if send_file:
            if gif:
                id = img[7:].split(".")[0]
                os.system(f"rm {img}")
                return True, id, error_message
            else:
                await context.send(f"{context.author.mention}\n{error_message[1:-1]}", file=discord.File(img))
                os.system(f"rm {img}")
        else:
            if gif:
                return False, "", error_message
            else:
                await context.send(f"{context.author.mention}\n{error_message[1:-1]}")

    bun_bot.run(KEY)
