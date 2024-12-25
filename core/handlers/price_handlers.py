import datetime, time

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core.keyboards.reply_keyboards import (
    start_keyboard,
    iphone_repair_keyboard,
    ipad_keyboard,
    ipad_repair_keyboard,
    iwatch_repair_keyboard,
    glass_repair_brand_list_keyboard,
    glass_repair_brand_list_iphone_sub_keyboard,
    iphone_sub_cat_1
)

from core.states.Prices_State import PriceState
from core.utils.commands import set_commands
from services.DatabaseService import JSONService

router = Router()
jsdb = JSONService()

# Список всех допустимых кнопок для проверки
valid_buttons = [
    "📱 Ремонт iPhone", "🪶 Ремонт iPad", "⌚️ Ремонт iWatch", "🫧 Переклейка",
    "🔬 Компонентные работы", "📲 Замена дисплея", "🛡️ Замена корпуса", "⚡ Шлейф зарядки",
    "🎥 Замена камеры", "🔋 Замена АКБ", "🔄 Сброс циклов АКБ", "🔙 Назад",
    "🖥️ iPad Series", "🪶 iPad Air Series", "📱 iPad Pro Series", "🔎 iPad Mini Series",
    "🖼️ Стекло дисплея", "🛡️ Стекло корпуса", "📷 Стекло камеры", "📐 Рамка дисплея",
    "📱 iPhone", "🖥️ iPad", "⌚️ iWatch", "📱 Samsung", "📱 Xiaomi", "📱 Honor",
    "🔧 Восстановление", "⚙️ SWAP", "🔙 Назад",
    "🫥 FaceID", "🔬 Компонентные работы", "📲 Замена дисплея", "🛡️ Замена корпуса",
    "⚡ Шлейф зарядки", "🎥 Замена камеры", "🔋 Замена АКБ", "🔄 Сброс циклов АКБ",
    "🔧 Восстановление", "⚙️ SWAP",
    "🖥️ iPad Series", "🪶 iPad Air Series", "📱 iPad Pro Series", "🔎 iPad Mini Series",
    "🖼️ Стекло дисплея", "🛡️ Стекло корпуса", "📷 Стекло камеры", "📐 Рамка дисплея",
    "📱 iPhone", "🖥️ iPad", "⌚️ iWatch", "📱 Samsung", "📱 Xiaomi", "📱 Honor"
]

# Проверка, является ли пользователь администратором
async def is_admin(user_id: int) -> bool:
    user_record = await jsdb.find_one('users', {'tg_id': user_id})
    return user_record and user_record.get('role') == 'admin'


@router.message(Command('dev'))
async def dev(message: Message):
    web_app_url = 'https://cwim-team.ru'  # Укажите URL вашего Web App

    # Создаем клавиатуру с кнопкой для Web App
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Register Page", web_app=WebAppInfo(url=web_app_url))]
        ]
    )

    # Отправляем сообщение с клавиатурой
    await message.answer('dev', reply_markup=keyboard)
# Обработчик команды start
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await jsdb.init()

    if await jsdb.test_connection():
        if not await jsdb.find_all('users', {}):
            await jsdb.create('users', {
                'tg_id': message.from_user.id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'last_activity': datetime.datetime.now().isoformat(),
                'role': 'admin'
            })
        elif not await jsdb.find_one('users', {'tg_id': int(message.from_user.id)}):
            await jsdb.create('users', {
                'tg_id': message.from_user.id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'last_activity': datetime.datetime.now().isoformat(),
                'role': 'user'
            })

    await state.set_data({"menu_stack": []})
    await message.answer(f'{message.from_user.username}, добро пожаловать! Чем я могу помочь?', reply_markup=start_keyboard, parse_mode='HTML')
    await set_commands(message.bot, 'start', 'Главное меню')

# Функция для получения цены
async def get_price(menu_stack, message: Message, is_admin: bool):
    # Формируем запрос по категориям
    request = " ".join(menu_stack)
    price_data = await jsdb.find_one('prices', {'category': request})

    if not price_data:
        if is_admin:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Добавить", callback_data="add_price")]]
            )
            await message.answer(
                "Тут можно вставить прайс, или любое другое сообщение!. Хотите добавить?", 
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            ...
        return None

    # Текст прайса
    price = price_data['price']

    # Форматирование текста
    if is_admin:
        # Администратор видит название категории и текст прайса
        price_text = (
            f"<b>Категория:</b> {menu_stack[0]} - {menu_stack[-1]}\n"
            f"<b>Прайс:</b>\n\n{price}"
        )
    else:
        # Пользователь видит только текст прайса
        price_text = (
            f"<b>Категория:</b> {menu_stack[0]} - {menu_stack[-1]}\n"
            f"<b>Прайс:</b>\n\n{price}"
        )

    # Отправка сообщения
    # await message.answer(price_text, parse_mode='HTML')
    return price_text


@router.callback_query(F.data == "add_price")
async def add_price_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст прайса для категории:", parse_mode='HTML')
    await state.update_data(price_category=" ".join((await state.get_data()).get("menu_stack", [])))
    await state.set_state(PriceState.price_message)
    await callback.answer()

# Обработчик изменения прайса
@router.message(F.text != "" and PriceState.price_message)
async def save_price_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    category = state_data.get("price_category")
    price_id = await jsdb.find_one('prices', {'category': category})
    
    # Проверяем, есть ли уже прайс для этой категории
    existing_price = await jsdb.find_one('prices', {'category': category})
    if existing_price:
        # Если прайс существует, обновляем его
        await jsdb.update('prices', price_id.get('id'), {'price': message.html_text})
        await message.reply("Прайс успешно обновлён!", parse_mode='HTML', reply_markup=start_keyboard)
    else:
        # Если прайс для этой категории отсутствует, создаём новый
        await jsdb.create('prices', {'category': category, 'price': message.html_text})
        await message.reply("Прайс успешно сохранён!", parse_mode='HTML', reply_markup=start_keyboard)

    await state.clear()

# Обработчик редактирования прайса
@router.callback_query(F.data == "edit_price")
async def edit_price_handler(callback: CallbackQuery, state: FSMContext):
    menu_stack = (await state.get_data()).get("menu_stack", [])
    category = " ".join(menu_stack)
    await callback.answer()
    
    # Проверяем, есть ли уже прайс для этой категории
    price_data = await jsdb.find_one('prices', {'category': category})
    
    if price_data:
        await callback.message.answer(f"Текущий прайс для категории <b>{category}</b>: {price_data['price']}. Напишите новый прайс.", parse_mode='HTML')
        await state.update_data(price_category=category)
        await state.set_state(PriceState.price_message)
    else:
        # Если прайс отсутствует, предлагаем добавить его
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Добавить прайс", callback_data="add_price")]]
        )
        await callback.message.answer(f"Прайс в категории <b>{category}</b> не указан. Хотите добавить новый прайс?", reply_markup=keyboard, parse_mode='HTML')

@router.message(F.text != "")
async def message_handler(message: Message, state: FSMContext):
    user_data = await state.get_data()
    menu_stack = user_data.get("menu_stack", [])

    if message.text not in valid_buttons:
        return
    if message.text != "🔙 Назад":
        menu_stack.append(message.text)
        await state.update_data(menu_stack=menu_stack)


    if message.text != "🔙 Назад":
        menu_stack.append(message.text)
        await state.update_data(menu_stack=menu_stack)

    is_admin_flag = await is_admin(message.from_user.id)
    price_data = await get_price(menu_stack, message, is_admin_flag)
    
    if price_data:
        if is_admin_flag:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Изменить прайс", callback_data="edit_price")]]
            )
            await message.reply(price_data, parse_mode='HTML', reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Напишите нам", url="https://t.me/okkpedantnsk")]]
            )
            await message.answer(price_data, parse_mode='HTML', reply_markup=keyboard)

    if message.text in ["📱 Ремонт iPhone", "🪶 Ремонт iPad", "⌚️ Ремонт iWatch", "🫧 Переклейка"]:
        if message.text == "📱 Ремонт iPhone":
            await message.reply("Выберите категорию", reply_markup=iphone_repair_keyboard)
        elif message.text == "🪶 Ремонт iPad":
            await message.reply("Выберите категорию", reply_markup=ipad_keyboard)
        elif message.text == "⌚️ Ремонт iWatch":
            await message.reply("Выберите категорию", reply_markup=iwatch_repair_keyboard)
        elif message.text == "🫧 Переклейка":
            await message.reply("Выберите бренд устройства", reply_markup=glass_repair_brand_list_keyboard)
        return

    if message.text == "🔬 Компонентные работы":
        await message.reply("Выберите подкатегорию", reply_markup=iphone_sub_cat_1)
        return

    if message.text == "📱 iPhone":
        await message.reply("Что будем переклеивать?", reply_markup=glass_repair_brand_list_iphone_sub_keyboard)
        return

    if message.text == "🔙 Назад":
        if menu_stack:
            menu_stack.pop()
        await state.update_data(menu_stack=menu_stack)

        if not menu_stack:
            await message.reply("Выберите категорию", reply_markup=start_keyboard)
        else:
            previous_menu = menu_stack[-1]
            if previous_menu == "📱 Ремонт iPhone":
                await message.reply("Выберите категорию", reply_markup=iphone_repair_keyboard)
            elif previous_menu == "🪶 Ремонт iPad":
                await message.reply("Выберите категорию", reply_markup=ipad_keyboard)
            elif previous_menu == "⌚️ Ремонт iWatch":
                await message.reply("Выберите категорию", reply_markup=iwatch_repair_keyboard)
            elif previous_menu == "🫧 Переклейка":
                await message.reply("Выберите бренд устройства", reply_markup=glass_repair_brand_list_keyboard)

    return