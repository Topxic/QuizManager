import logging
import uuid
import mysql.connector
from util import *

from config import DB_CONFIG

QUIZ_TABLE = 'quiz'
ANSWER_TABLE = 'answer'
GIVEN_ANSWER_TABLE = 'given_answer'

log = logging.getLogger(__name__)


def create_tables():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        with open('create-db.sql', 'r') as file:
            sql_script = file.read().replace('\n', ' ')
            for subscript in sql_script.split(";"):
                log.debug(subscript)
                cursor.execute(subscript)
            connection.commit()
    except Exception as e:
        log.error('Error creating database tables: %s', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_ttl():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = (
            "UPDATE {} SET time_to_live = GREATEST(0, time_to_live - 5) WHERE time_to_live > 0").format(QUIZ_TABLE)
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        log.error('Error updating time to live: %s', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


async def create_game(quiz_request: QuizRequest):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        quiz_id = uuid.uuid4()
        query = ("INSERT INTO {} (quiz_id, message_id, channel_id, creator_id, question, time_to_live, closed)"
                 "VALUES (UNHEX(%s), %s, %s, %s, %s, %s, %s)").format(QUIZ_TABLE)
        cursor.execute(query, (
            quiz_id.hex,
            quiz_request.message_id,
            quiz_request.channel_id,
            quiz_request.creator_id,
            quiz_request.question,
            quiz_request.ttl,
            quiz_request.ttl > 0
        ))
        log.debug("Persisted new quiz: %s", quiz_id.hex)

        for i in range(len(quiz_request.emojis)):
            answer_id = uuid.uuid4()
            query = ("INSERT INTO {} (answer_id, quiz_id, answer, correct)"
                 "VALUES (UNHEX(%s), UNHEX(%s), %s, %s)").format(ANSWER_TABLE)
            cursor.execute(query, (
                answer_id.hex,
                quiz_id.hex,
                quiz_request.answers[i],
                quiz_request.emojis[i] in quiz_request.solutions
            ))
            log.debug("Persisted new answer: %s", answer_id.hex)

        connection.commit()
    except Exception as e:
        log.error('Error persisting quiz entity: %s', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
