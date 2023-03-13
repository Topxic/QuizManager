import os
import discord
import dotenv

dotenv.load_dotenv('./secrets.env')

COMMAND_PREFIX = '?'
BOT_DESCRIPTION = 'Quiz moderation: This bot creates and moderates quiz questions with a lifetime set by the user. Furhtermore, it provides commands for player statistics. Use ' + \
    COMMAND_PREFIX + 'help to get the list of possible commands'
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
EMBED_COLOR = discord.Color.orange()
UPDATE_INTERVAL = 20

DB_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_SECRET'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE'),
    'raise_on_warnings': True,
    'autocommit': True,
    'pool_size': 5
}

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

CREATE_DESCRIPTION = 'Create a quiz question. \n\n Pass information line-wise: \nQuestion, active time, correct answer answer1 answer2 ... \n\nExample: \n' + \
    COMMAND_PREFIX + 'create How many fingers am I showing? \n30 1 0 0 0 \n🇧 \n🇦  You show 1 finger \n🇧  You show 2 fingers \n🇨  You show 3 fingers'

PLAYER_DESCRIPTION = 'Request stats of player that send the command.'

CHANNEL_DESCRIPTION = 'Request stats of the scoped channel including number of quizzes and scoreboard'
