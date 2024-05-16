import logging
import random
import redis
import json

from functools import partial
from environs import Env
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

from keyboards import get_main_keyboard
from get_quiz_content import load_quiz_content


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Здравствуйте!",
                             reply_markup=get_main_keyboard(),
                             )


def echo(update: Update, context: CallbackContext, db):
    if update.message.text == 'Новый вопрос':
        quiz_content = load_quiz_content()
        question = random.choice(quiz_content)
        question_json = json.dumps(question)
        db.set(str(update.effective_chat.id), question_json)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=question[0],
                                 reply_markup=get_main_keyboard(),
                                 )
    else:
        question = json.loads(db.get(str(update.effective_chat.id)))
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=question[1],
                                 reply_markup=get_main_keyboard(),
                                )


def new_question(update: Update, context: CallbackContext):
    quiz_content = load_quiz_content()

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Ваш вопрос принят. Мы ответим в ближайшее время.',
                             reply_markup=get_main_keyboard(),
                            )

def start_tg_bot(token, logger, db):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), partial(echo, db=db))

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)

    logger.info('Start telegram bot')
    updater.start_polling()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    logger = logging.getLogger(__name__)
    token = env('TG_BOT_API')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    r = redis.Redis(host=env.str('REDIS_HOST'),
                    port=17869,
                    db=0,
                    password=env.str('REDIS_PASSWORD'),
                    )

    start_tg_bot(token, logger, db=r)
