from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главная клавиатура
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📱 Ремонт iPhone"),
            KeyboardButton(text="🪶 Ремонт iPad")
        ],
        [
            KeyboardButton(text="⌚️ Ремонт iWatch"),
            KeyboardButton(text="🫧 Переклейка")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Клавиатура для ремонта iPhone
iphone_repair_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🫥 FaceID"),
            KeyboardButton(text="🔬 Компонентные работы")
        ],
        [
            KeyboardButton(text="📲 Замена дисплея"),
            KeyboardButton(text="🛡️ Замена корпуса")
        ],
        [
            KeyboardButton(text="⚡ Шлейф зарядки"),
            KeyboardButton(text="🎥 Замена камеры")
        ],
        [
            KeyboardButton(text="🔋 Замена АКБ"),
            KeyboardButton(text="🔄 Сброс циклов АКБ")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Подкатегория для ремонта iPhone
iphone_sub_cat_1 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔧 Восстановление"),
            KeyboardButton(text="⚙️ SWAP")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Клавиатура для ремонта iPad
ipad_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🖥️ iPad Series"),
            KeyboardButton(text="🪶 iPad Air Series")
        ],
        [
            KeyboardButton(text="📱 iPad Pro Series"),
            KeyboardButton(text="🔎 iPad Mini Series")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Клавиатура для ремонта iPad
ipad_repair_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔧 Замена тачскрина"),
            KeyboardButton(text="💻 Замена дисплея")
        ],
        [
            KeyboardButton(text="🔋 Аккумулятор"),
            KeyboardButton(text="🔬 Ремонт CPU")
        ],
        [
            KeyboardButton(text="⚡ Замена шлейфа зарядки"),
        ],
        [
            KeyboardButton(text="🔌 Замена контроллера заряда"),
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Клавиатура для ремонта iWatch
iwatch_repair_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📱 Замена дисплея"),
            KeyboardButton(text="🔋 Замена АКБ")
        ],
        [
            KeyboardButton(text="💧 Чистка от влаги"),
            KeyboardButton(text="💾 Прошивка")
        ],
        [
            KeyboardButton(text="🧑‍🔧 Стекло корпуса"),
            KeyboardButton(text="🎧 Digital Crown")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Клавиатура для выбора бренда стекла
glass_repair_brand_list_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📱 iPhone"),
            KeyboardButton(text="🖥️ iPad"),
        ],
        [
            KeyboardButton(text="⌚️ iWatch"),
            KeyboardButton(text="📱 Samsung")
        ],
        [
            KeyboardButton(text="📱 Xiaomi"),
            KeyboardButton(text="📱 Honor")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)

# Подкатегория для стекла дисплея iPhone
glass_repair_brand_list_iphone_sub_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🖼️ Стекло дисплея"),
            KeyboardButton(text="🛡️ Стекло корпуса")
        ],
        [
            KeyboardButton(text="📷 Стекло камеры"),
            KeyboardButton(text="📐 Рамка дисплея")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    row_width=2,
)
