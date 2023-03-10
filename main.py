import discord
import logging
import logging.config

from discord.ext import tasks
from discord.ext.commands import *
from config import *
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
bot = Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)
    for reaction in message.reactions:
        # Skip reaction that is added during this call
        if payload.emoji.name == reaction.emoji:
            continue
        async for user in reaction.users():
            # Ignore bot reactions
            if user.bot:
                continue
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
        embed.description = 'Quiz valid for: ' + \
            seconds_to_string(time_to_live)
        await message.edit(embed=embed)

    for quiz_row in terminated:
        quiz_id = quiz_row[0]
        message_id = quiz_row[1]
        channel_id = quiz_row[2]

        # Fetch quiz embed
        channel = bot.get_channel(channel_id)
        message: discord.Message = await channel.fetch_message(message_id)
        embed: discord.Embed = message.embeds[0]

        answer_entities = get_answers(quiz_id)
        # Create emoji-answer_id lookup
        answer_lookup = {}
        for answer_entity in answer_entities:
            answer_id = answer_entity[0]
            emoji = answer_entity[1]
            answer_str = answer_entity[2]
            correct = answer_entity[3]
            answer_lookup[emoji] = (answer_id, answer_str, correct)

        # Process user reactions
        given_answers = []
        for reaction in message.reactions:
            async for user in reaction.users():
                # Skip bots
                if user.bot:
                    continue

                answer = answer_lookup[reaction.emoji]
                given_answers.append((quiz_id, answer[0], user.id))

        persist_given_answers(given_answers)

        embed.description = "Quiz ended correct answers:\n" + '\n'.join(
            [answer[1] for answer in answer_lookup.values() if answer[2]])
        await message.edit(embed=embed)


@bot.command(name="create")
async def create_quiz(ctx: Context, *, request: QuizRequest):
    # Build quiz embed
    embed = discord.Embed(
        title=request.question,
        description='Quiz valid for: ' + seconds_to_string(request.ttl),
        color=discord.Color.orange()
    )
    embed.add_field(name='Answers', value='\n'.join(
        [emoji + ' ' + text for emoji, text in zip(
            request.emojis, request.answers)]
    ), inline=False)
    quiz = await ctx.send(embed=embed)

    # Persist quiz entity
    request.message_id = quiz.id
    create_game(request)

    # Add emoji reactions for voting
    for emoji in request.emojis:
        await quiz.add_reaction(emoji)

    # Delete command message
    await ctx.message.delete(delay=5)


@bot.command(name="score")
async def score(ctx: Context):
    user_id = ctx.author.id
    channel_id = ctx.channel.id
    score = get_score(user_id, channel_id)

    embed = discord.Embed(
        title="Stats for player " + ctx.author.name,
        color=discord.Color.orange()
    )
    embed.add_field(name='Score', value=score, inline=False)

    stats = await ctx.send(embed=embed)

    # Delete command message
    await ctx.message.delete(delay=5)


@bot.command(name="leaderboard")
async def leaderboard(ctx: Context):
    channel_id = ctx.channel.id
    scores = get_scores(channel_id)

    embed = discord.Embed(
        title="Cannel leaderboard",
        color=discord.Color.orange()
    )
    for score in scores:
        player: discord.User = await bot.fetch_user(score[0])
        embed.add_field(name='Score for player ' + player.name, value=score[1], inline=False)

    stats = await ctx.send(embed=embed)

    # Delete command message
    await ctx.message.delete(delay=5)
            

@bot.event
async def on_ready():
    log.info('QuizManager ready')
    update_loop.start()


bot.run(DISCORD_TOKEN, log_handler=None)  # Use root logger
