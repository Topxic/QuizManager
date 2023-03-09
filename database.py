import logging
import uuid
import mysql.connector
from util import *

from config import DB_CONFIG, UPDATE_INTERVAL

QUIZ_TABLE = 'quiz'
ANSWER_TABLE = 'answer'
GIVEN_ANSWER_TABLE = 'given_answer'

log = logging.getLogger(__name__)


def get_correct_answers(quiz_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = ("SELECT answer "
                 "FROM {} "
                 "WHERE quiz_id = UNHEX('{}') AND correct = 1").format(ANSWER_TABLE, quiz_id.hex)
        cursor.execute(query)
        answers = cursor.fetchall()
        return answers
    except Exception as e:
        log.error('Error selecting answers for quiz %s: %s', quiz_id, e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


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
        query = ("UPDATE {} "
                 "SET time_to_live = GREATEST(0, time_to_live - {}) "
                 "WHERE time_to_live > 0 AND finished = 1").format(QUIZ_TABLE, UPDATE_INTERVAL)
        cursor.execute(query)

        query = ("SELECT quiz_id, message_id, channel_id "
                 "FROM {} "
                 "WHERE time_to_live = 0 AND finished = 1").format(QUIZ_TABLE)
        cursor.execute(query)
        terminated = cursor.fetchall()

        query = ("SELECT message_id, channel_id, time_to_live "
                 "FROM {} "
                 "WHERE time_to_live > 0 AND finished = 1").format(QUIZ_TABLE)
        cursor.execute(query)
        running = cursor.fetchall()

        query = ("UPDATE {} "
                 "SET finished = 0 "
                 "WHERE time_to_live = 0 AND finished = 1").format(QUIZ_TABLE)
        
        cursor.execute(query)
        connection.commit()
        return (running, terminated)
    except Exception as e:
        log.error('Error updating time to live: %s', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def create_game(quiz_request: QuizRequest):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        quiz_id = uuid.uuid4()
        query = ("INSERT INTO {} (quiz_id, message_id, channel_id, creator_id, question, time_to_live, finished) "
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
            query = ("INSERT INTO {} (answer_id, quiz_id, answer, correct) "
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
