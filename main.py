import os
import time
import discord
import logging

import sqlite3 as sql

from discord.ext.commands import *
from dotenv import load_dotenv

from quiz import *
from util import *

CREATE_USAGE = """
**create How many finger am I showing?
30 1 0 0 0
🇧 
🇦  You show 1 finger
🇧  You show 2 fingers
🇨  You show 3 fingers"""

# Setup logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Load environment variables
load_dotenv('./secrets.env')
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up database
con = sql.connect('database.db')

# Create bot client
intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix='**', intents=intents)


@bot.command(name="create")
async def create_quiz(ctx: Context, *, quiz: Quiz, user: discord.User, channel: discord.TextChannel):
    # Build poll embed
    embed = discord.Embed(
        title='Quiz',
        description='Quiz valid for: ' + cron_to_string(quiz.cron),
        color=discord.Color.orange()
    )
    embed.add_field(name='Question', value=quiz.question, inline=False)
    embed.add_field(name='Answers', value=quiz.answers, inline=False)

    poll = await ctx.send(embed=embed)

    # Add emoji reactions for voting
    for emoji in quiz.emojis:
        await poll.add_reaction(emoji)

    # Wait poll time
    while quiz.ttl > 0:
        time.sleep(min(5, quiz.ttl))
        quiz.ttl -= 5
        if quiz.ttl > 0:
            embed.description = 'Poll valid for: ' + \
                seconds_to_string(quiz.ttl)
        else:
            embed.description = 'Poll finished. Correct answer: '
        await poll.edit(embed=embed)

    # Mark poll as finished and collect result
    for emoji in quiz.emojis:
        updated_poll = await ctx.fetch_message(poll.id)
        reactions = discord.utils.get(updated_poll.reactions, emoji=emoji)
        print(emoji, reactions.count)


@bot.event
async def on_ready():
    log.info('QuizManager ready')

bot.run(TOKEN)
