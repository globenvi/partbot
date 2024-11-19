from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def get_profile_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить Аватар", callback_data="change_avatar")
            ],
            [
                InlineKeyboardButton(text="Изменить Ник", callback_data="change_nick"),
                InlineKeyboardButton(text="Изменить Подпись", callback_data="change_såignature")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_to_main")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        row_width=2,
    )

def get_open_web_ui_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='⚙️ Открыть GPT',
                    web_app=WebAppInfo(url='https://cwim-team.ru:8080')
                )
            ]
        ]
    )
