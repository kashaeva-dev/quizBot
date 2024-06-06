import argparse
import json
import logging
import random
import re

import redis
import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from get_quiz_content import load_quiz_content
from vk_keyboards import get_main_keyboard

logger = logging.getLogger(__name__)


def handle_new_question_request(event, vk_api, db, filepath, logger=logger):
    quiz_content = load_quiz_content(filepath)
    question = random.choice(quiz_content)
    question_json = json.dumps(question)
    db.set(str(event.user_id), question_json)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question[0],
        random_id=random.randint(1, 1000),
        keyboard=get_main_keyboard(),
    )


def handle_surrender_request(event, vk_api, db, filepath, logger=logger):
    question = json.loads(db.get(str(event.user_id)))
    logger.info(f'User {event.user_id} surrendered. Answer: {question[1]}')
    vk_api.messages.send(
        user_id=event.user_id,
        message=question[1],
        random_id=random.randint(1, 1000),
        keyboard=get_main_keyboard(),
    )
    handle_new_question_request(event, vk_api, db, filepath=filepath)


def handle_answer_checking(event, vk_api, db, logger=logger):
    if (question := db.get(str(event.user_id))) is None:
        text = 'Чтобы начать викторину нажми «Новый вопрос»'
        vk_api.messages.send(
            user_id=event.user_id,
            message=text,
            random_id=random.randint(1, 1000),
            keyboard=get_main_keyboard(),
        )
        return
    question = json.loads(question)
    answer = re.split(r'[.(]', question[1])[0].lower()

    if answer == event.text.lower():
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000),
        keyboard=get_main_keyboard(),
    )


def handle_conversation(event, vk_api, db, filepath, logger=logger):
    if event.text == 'Новый вопрос':
        handle_new_question_request(event, vk_api, db, filepath=filepath)
    elif event.text == 'Сдаться':
        handle_surrender_request(event, vk_api, db, filepath=filepath)
    else:
        handle_answer_checking(event, vk_api, db)


def start_vk_bot(token, logger, db, filepath):
    logger.info('Start vk bot')

    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_conversation(event, vk_api, db=db, filepath=filepath)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="Start vk bot",
    )
    parser.add_argument('--file',
                        default='../quizBot/quiz_content.txt',
                        help='Path to file with quiz content',
                        )
    return parser


if __name__ == "__main__":
    env = Env()
    env.read_env()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    vk_token = env.str('VK_BOT_API')

    parser = create_parser()
    args = parser.parse_args()

    redis_host = env.str('REDIS_HOST')
    redis_port = env.int('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')

    redis_db = redis.Redis(host=redis_host,
                           port=redis_port,
                           db=0,
                           password=redis_password,
                           )

    start_vk_bot(vk_token, logger, redis_db, filepath=args.file)
