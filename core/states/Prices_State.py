from aiogram.fsm.state import State, StatesGroup


class PriceState(StatesGroup):
    category = State()
    subcategory = State()
    price_message = State()