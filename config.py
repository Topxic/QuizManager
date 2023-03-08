import os
import dotenv

dotenv.load_dotenv('./secrets.env')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

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
            'level': 'INFO',
            'propagate': False
        }
    } 
}

CREATE_USAGE = """
**create How many fingers am I showing?
30 1 0 0 0
🇧 
🇦  You show 1 finger
🇧  You show 2 fingers
🇨  You show 3 fingers"""
