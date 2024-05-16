import logging
import random
import redis
import json
import re

from functools import partial
from environs import Env
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext, ConversationHandler

from keyboards import get_main_keyboard
from get_quiz_content import load_quiz_content


def start(update: Update, context: CallbackContext, db):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Здравствуйте!",
                             reply_markup=get_main_keyboard(),
                             )

    return 'REQUEST_QUESTION'


def handle_solution_attempt(update: Update, context: CallbackContext, db):
    question = json.loads(db.get(str(update.effective_chat.id)))
    answer = re.split(r'[.(]', question[1])[0].lower()
    logger.info(answer)
    logger.info(question[1])

    if answer == update.message.text.lower():
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 reply_markup=get_main_keyboard(),
                                 )

        return 'REQUEST_QUESTION'

    else:
        text='Неправильно… Попробуешь ещё раз?'
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 reply_markup=get_main_keyboard(),
                                 )

        return 'WAITING_ANSWER'


def handle_new_question_request(update: Update, context: CallbackContext, db):
    quiz_content = load_quiz_content()
    question = random.choice(quiz_content)
    question_json = json.dumps(question)
    db.set(str(update.effective_chat.id), question_json)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=question[0],
                             reply_markup=get_main_keyboard(),
                             )

    return 'WAITING_ANSWER'


def handle_surrender_request(update: Update, context: CallbackContext, db):
    question = json.loads(db.get(str(update.effective_chat.id)))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Ответ на этот вопрос: {question[1]}',
                             reply_markup=get_main_keyboard(),
                             )
    handle_new_question_request(update, context, db)


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(text='Пока!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def start_tg_bot(token, logger, db):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial(start, db=db))],

        states={
            'WAITING_ANSWER': [
                MessageHandler(Filters.text & (~Filters.command) & (~Filters.regex(r'^Сдаться$')),
                               partial(handle_solution_attempt,db=db)),
                MessageHandler(Filters.text & Filters.regex(r'^Сдаться$'),
                               partial(handle_surrender_request, db=db)),
            ],
            'REQUEST_QUESTION': [
                MessageHandler(Filters.text & Filters.regex(r'^Новый вопрос$'),
                               partial(handle_new_question_request, db=db)),
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

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
