from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

commands_list = []

async def set_commands(bot: Bot, command: str, description: str):
    global commands_list  # Используем глобальную переменную

    new_command = BotCommand(command=command, description=description)
    commands_list.append(new_command)  # Добавляем новую команду к списку

    await bot.set_my_commands(commands_list, BotCommandScopeDefault())

