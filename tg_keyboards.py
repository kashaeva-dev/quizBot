import telegram


def get_main_keyboard():
    main_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет'],
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

    return reply_markup
