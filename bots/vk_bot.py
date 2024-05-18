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


def handle_new_question_request(event, vk_api, db):
    quiz_content = load_quiz_content()
    question = random.choice(quiz_content)
    question_json = json.dumps(question)
    db.set(str(event.user_id), question_json)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question[0],
        random_id=random.randint(1, 1000),
        keyboard=get_main_keyboard(),
    )

def handle_surrender_request(event, vk_api, db):
    question = json.loads(db.get(str(event.user_id)))
    print(question[1])
    vk_api.messages.send(
        user_id=event.user_id,
        message=question[1],
        random_id=random.randint(1, 1000),
        keyboard=get_main_keyboard(),
    )
    handle_new_question_request(event, vk_api, db)


def handle_answer_checking(event, vk_api, db):
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


def handle_conversation(event, vk_api, db):
    if event.text == 'Новый вопрос':
        handle_new_question_request(event, vk_api, db)
    elif event.text == 'Сдаться':
        handle_surrender_request(event, vk_api, db)
    else:
        handle_answer_checking(event, vk_api, db)


def start_vk_bot(token, logger, db=0):
    logger.info('Start vk bot')

    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    r = redis.Redis(host=env.str('REDIS_HOST'),
                    port=17869,
                    db=0,
                    password=env.str('REDIS_PASSWORD'),
                    )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_conversation(event, vk_api, db=r)


if __name__ == "__main__":
    env = Env()
    env.read_env()

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    vk_token = env.str('VK_BOT_API')
    start_vk_bot(vk_token, logger)
