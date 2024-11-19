from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="😎 Профиль")
        ],
        [
            KeyboardButton(text="⚙ Настройки"),
            KeyboardButton(text='💊 Тех.Поддержка')
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
    selective=False,  # optional, defaults to False
)