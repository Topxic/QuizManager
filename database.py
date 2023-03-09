import logging
import mysql.connector
from util import *

from config import DB_CONFIG, UPDATE_INTERVAL

QUIZ_TABLE = 'quiz'
ANSWER_TABLE = 'answer'
GIVEN_ANSWER_TABLE = 'given_answer'

log = logging.getLogger(__name__)


def persist_given_answers(given_answers):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        for given_answer in given_answers:
            query = ("INSERT INTO {} (quiz_id, answer_id, player_id) "
                     "VALUES (%s, %s, %s)").format(GIVEN_ANSWER_TABLE)
            cursor.execute(query, (
                given_answer[0],
                given_answer[1],
                given_answer[2]
            ))
            given_answer_id = cursor.lastrowid
            log.debug("Persisted new given answer: %s", given_answer_id)

        connection.commit()
    except Exception as e:
        log.error('Error persisting given answer entity: %s', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_answers(quiz_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = ("SELECT answer_id, emoji, answer, correct "
                 "FROM {} "
                 "WHERE quiz_id = {}").format(ANSWER_TABLE, quiz_id)
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

        query = ("INSERT INTO {} (message_id, channel_id, creator_id, question, time_to_live, finished) "
                 "VALUES (%s, %s, %s, %s, %s, %s)").format(QUIZ_TABLE)
        cursor.execute(query, (
            quiz_request.message_id,
            quiz_request.channel_id,
            quiz_request.creator_id,
            quiz_request.question,
            quiz_request.ttl,
            quiz_request.ttl > 0
        ))
        quiz_id = cursor.lastrowid
        log.debug("Persisted new quiz: %s", quiz_id)

        for i in range(len(quiz_request.emojis)):
            query = ("INSERT INTO {} (quiz_id, emoji, answer, correct) "
                 "VALUES (%s, %s, %s, %s)").format(ANSWER_TABLE)
            cursor.execute(query, (
                quiz_id,
                quiz_request.emojis[i],
                quiz_request.answers[i],
                quiz_request.emojis[i] in quiz_request.solutions
            ))
            log.debug("Persisted new answer: %s", cursor.lastrowid)

        connection.commit()
    except Exception as e:
        log.error('Error persisting quiz entity: %s', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
