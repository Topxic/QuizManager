import time
import uuid
import threading
import discord
import logging
import logging.config

from discord.ext.commands import *
from config import DISCORD_TOKEN, LOGGING_CONFIG, UPDATE_INTERVAL
from database import create_game, create_tables, update_ttl

from util import *

# Setup logger
logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)

# Setup database
create_tables()

# Create bot client
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = Bot(command_prefix="**", intents=intents)


@bot.event
async def on_raw_reaction_add(payload):
    # Ignore bot reactions
    if bot.user.id == payload.user_id:
        return
    
    channel = bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)
    for reaction in message.reactions:
        # Skip reaction that is added during this call
        if payload.emoji.name == reaction.emoji:
            continue
        async for user in reaction.users():
            if user.id == payload.user_id:
                await message.remove_reaction(reaction, discord.Object(user.id))       


def update():
    while True:
        terminated = update_ttl()
        for quiz_row in terminated:
            message_id = quiz_row[0]
            channel_id = quiz_row[1]
            creator_id = quiz_row[2]
            log.info("Quiz has terminated (%i, %i, %i)",
                     message_id,
                     channel_id,
                     creator_id)
            
            # Mark poll as finished and collect result
            # for emoji in quiz.emojis:
            #     updated_poll = await ctx.fetch_message(poll.id)
            #     reactions = discord.utils.get(updated_poll.reactions, emoji=emoji)
            #     print(emoji, reactions.count)
        time.sleep(UPDATE_INTERVAL)


@bot.command(name="create")
async def create_quiz(ctx: Context, *, quiz_request: QuizRequest):
    # Persist quiz entity
    await create_game(quiz_request)

    # Build poll embed
    embed = discord.Embed(
        title='Quiz',
        description='Quiz valid for: ' + seconds_to_string(quiz_request.ttl),
        color=discord.Color.orange()
    )
    embed.add_field(name='Question', value=quiz_request.question, inline=False)
    embed.add_field(name='Answers', value='\n'.join(
        quiz_request.answers), inline=False)

    poll = await ctx.send(embed=embed)

    # Add emoji reactions for voting
    for emoji in quiz_request.emojis:
        await poll.add_reaction(emoji)


@bot.event
async def on_ready():
    log.info('QuizManager ready')

# Start update thread
thread = threading.Thread(target=update)
thread.start()

bot.run(DISCORD_TOKEN, log_handler=None)  # Use root logger
