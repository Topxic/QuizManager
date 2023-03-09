import discord
import logging
import logging.config

from discord.ext import tasks
from discord.ext.commands import *
from config import DISCORD_TOKEN, LOGGING_CONFIG, UPDATE_INTERVAL
from database import *

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


@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_loop():
    (running, terminated) = update_ttl()

    for quiz_row in running:
        message_id = quiz_row[0]
        channel_id = quiz_row[1]
        time_to_live = quiz_row[2]
        channel = bot.get_channel(channel_id)
        message: discord.Message = await channel.fetch_message(message_id)
        embed: discord.Embed = message.embeds[0]
        embed.description = 'Quiz valid for: ' + seconds_to_string(time_to_live)
        await message.edit(embed=embed)
    
    for quiz_row in terminated:
        quiz_id = uuid.UUID(bytes=bytes(quiz_row[0]))
        message_id = quiz_row[1]
        channel_id = quiz_row[2]

        answers = get_correct_answers(quiz_id)
        answers = [x[0] for x in answers]

        channel = bot.get_channel(channel_id)
        message: discord.Message = await channel.fetch_message(message_id)
        embed: discord.Embed = message.embeds[0]
        embed.description = "Quiz ended correct answers:\n" + '\n'.join(answers)
        await message.edit(embed=embed)


@bot.command(name="create")
async def create_quiz(ctx: Context, *, quiz_request: QuizRequest):
    # Build quiz embed
    embed = discord.Embed(
        title=quiz_request.question,
        description='Quiz valid for: ' + seconds_to_string(quiz_request.ttl),
        color=discord.Color.orange()
    )
    embed.add_field(name='Answers', value='\n'.join(
        quiz_request.answers), inline=False)
    quiz = await ctx.send(embed=embed)

    # Persist quiz entity
    quiz_request.message_id = quiz.id
    create_game(quiz_request)

    # Add emoji reactions for voting
    for emoji in quiz_request.emojis:
        await quiz.add_reaction(emoji)


@bot.event
async def on_ready():
    log.info('QuizManager ready')
    update_loop.start()


bot.run(DISCORD_TOKEN, log_handler=None)  # Use root logger
