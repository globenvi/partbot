import os
import asyncio
import logging
from tqdm import tqdm
from colorama import Fore, Style

from aiogram import Bot, Dispatcher
from config_reader import config

from services.DatabaseService import JSONService

from services.LoggingService import LoggerService
from services.WebViewService import WebViewService
from services.PluginLoader import PluginLoader
from services.HandlerLoader import HandlerLoader

logging.basicConfig(level=logging.INFO)

db_service = JSONService()

async def initialize_services():
    """Инициализация всех сервисов."""
    # Логирование
    logger_service = LoggerService()
    logger_service.log_system("Инициализация логгирования начата.")

    # Инициализация WebView
    webview_service = WebViewService()
    logger_service.log_system("Инициализация WebView начата.")

    # Список сервисов
    services = [logger_service, webview_service]

    # Запуск сервисов с прогрессом
    for service in tqdm(services, desc="Загрузка сервисов", colour="green"):
        if isinstance(service, WebViewService):
            # Для WebView используем subprocess, так как это не асинхронный процесс
            service.start_server()
        await asyncio.sleep(0.5)  # Задержка для асинхронной загрузки сервисов

    # Логируем успешный запуск всех сервисов
    logger_service.log_system("Все сервисы успешно запущены.")
    return logger_service

async def load_handlers_and_modules(logger_service, dp):
    """Загрузка хэндлеров и модулей."""
    # Загружаем хэндлеры
    handler_loader = HandlerLoader(dp, handlers_dir='core/handlers')
    await handler_loader.load_handlers()  # Асинхронно загружаем и регистрируем обработчики

    logger_service.log_system("Хэндлеры успешно загружены.")
    
    # Загружаем модули через PluginLoader
    plugin_loader = PluginLoader(dp, logger_service, db_service)
    await plugin_loader.load_plugins()  # Загрузка модулей с выводом в консоль

async def main():
    # Инициализация сервисов
    logger_service = await initialize_services()

    # Запуск бота только после успешной инициализации всех сервисов
    logger_service.log_system("Запуск бота начат.")
    bot = Bot(config.bots.token)
    dp = Dispatcher()

    # Логируем успешную инициализацию бота
    logger_service.log_bot_activity("Бот успешно инициализирован.")

    # Загружаем handlers и modules
    await load_handlers_and_modules(logger_service, dp)

    # Запуск бота
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
