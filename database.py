import mysql.connector
import logging
from pypika import Table, MySQLQuery
from util import *

from config import DB_CONFIG

log = logging.getLogger(__name__)


def create_tables():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        with open('create-db.sql', 'r') as file:
            sql_script = file.read().replace('\n', ' ')
            for subscript in sql_script.split(";"):
                cursor.execute(subscript)
            connection.commit()
    except mysql.connector.Error as e:
        log.error('Error while connecting to MySQL', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


async def create_game(quiz_request: QuizRequest):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        quiz_table = Table('quiz')
        query = MySQLQuery.into(quiz_table).insert(
            quiz_request.message_id,
            quiz_request.channel_id,
            quiz_request.creator_id,
            quiz_request.question,
            quiz_request.ttl
        )
        cursor.execute(str(query))
        answer_table = Table('answer')
        for i in range(len(quiz_request.emojis)):
            query = MySQLQuery.into(answer_table).insert(
                quiz_request.message_id,
                quiz_request.answers[i],
                quiz_request.emojis[i] in quiz_request.solutions
            )
            cursor.execute(str(query))
        connection.commit()
    except Exception as e:
        log.error('Error while connecting to MySQL', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
