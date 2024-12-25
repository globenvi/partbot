import importlib
import os
import logging
from pathlib import Path
from aiogram import Router

logger = logging.getLogger(__name__)

class HandlerLoader:
    def __init__(self, router: Router, handlers_dir: str):
        """
        :param router: Главный роутер, в который будут добавляться все обработчики.
        :param handlers_dir: Путь к директории с обработчиками.
        """
        self.router = router
        self.handlers_dir = handlers_dir

    async def load_handlers(self):
        """
        Асинхронно загружает все модули из директории handlers и регистрирует их роутеры.
        """
        handler_files = self._get_handler_files()

        # Асинхронная загрузка всех обработчиков
        for handler_file in handler_files:
            await self._import_and_register_router(handler_file)

    def _get_handler_files(self):
        """
        Получает все файлы Python в папке с хэндлерами, кроме __init__.py.
        """
        handler_files = [
            f.stem for f in Path(self.handlers_dir).glob('*.py') if f.stem != '__init__'
        ]
        return handler_files

    async def _import_and_register_router(self, handler_file: str):
        """
        Импортирует модуль и регистрирует его роутер в основном роутере.
        """
        try:
            # Динамически импортируем модуль
            module = importlib.import_module(f"core.handlers.{handler_file}")
            
            # Предполагаем, что в каждом модуле есть атрибут router
            router = getattr(module, 'router', None)

            if router:
                # Регистрируем роутер
                self.router.include_router(router)
                logger.info(f"Роутер из модуля {handler_file} успешно зарегистрирован.")
            else:
                logger.warning(f"В модуле {handler_file} не найден атрибут 'router'.")
        
        except Exception as e:
            logger.error(f"Ошибка при загрузке обработчика {handler_file}: {e}")
