from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def get_main_keyboard():
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('Мой счет')

    return keyboard.get_keyboard()
