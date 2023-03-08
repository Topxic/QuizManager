import time
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
bot = Bot(command_prefix="**", intents=intents)


def update():
    while True:
        terminated_quizzes = update_ttl()
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
    embed.add_field(name='Answers', value=quiz_request.answers, inline=False)

    poll = await ctx.send(embed=embed)

    # Add emoji reactions for voting
    for emoji in quiz_request.emojis:
        await poll.add_reaction(emoji)


    # Wait poll time
#    while quiz.ttl > 0:
#        time.sleep(min(5, quiz.ttl))
#        quiz.ttl -= 5
#        if quiz.ttl > 0:
#            embed.description = 'Poll valid for: ' + \
#                seconds_to_string(quiz.ttl)
#        else:
#            embed.description = 'Poll finished. Correct answer: '
#        await poll.edit(embed=embed)
#
#    # Mark poll as finished and collect result
#    for emoji in quiz.emojis:
#        updated_poll = await ctx.fetch_message(poll.id)
#        reactions = discord.utils.get(updated_poll.reactions, emoji=emoji)
#        print(emoji, reactions.count)


@bot.event
async def on_ready():
    log.info('QuizManager ready')

# Start update thread
thread = threading.Thread(target=update)
thread.start()

bot.run(DISCORD_TOKEN, log_handler=None)  # Use root logger
