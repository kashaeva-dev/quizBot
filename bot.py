import logging

from environs import Env
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

from keyboards import get_main_keyboard


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Здравствуйте!",
                             reply_markup=get_main_keyboard(),
                             )


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text,
                             reply_markup=get_main_keyboard(),
                            )


def start_tg_bot(token, logger):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

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

    start_tg_bot(token, logger)
