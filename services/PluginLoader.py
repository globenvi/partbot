import os
import importlib
import asyncio
import re
from tqdm import tqdm
from services.LoggingService import LoggerService
from services.DatabaseService import JSONService

class PluginLoader:
    def __init__(self, dp, logger_service: LoggerService, db_service: JSONService):
        self.dp = dp
        self.logger_service = logger_service
        self.db_service = db_service  # Сервис для работы с базой данных

    async def load_plugins(self):
        """Загружает плагины асинхронно и добавляет их в Dispatcher, а также сохраняет их данные в БД."""
        if os.path.exists('modules'):
            module_files = [f[:-3] for f in os.listdir('modules') if f.endswith('.py')]
        else:
            module_files = []
            self.logger_service.log_system("Warning: 'modules' directory not found")
            print("Warning: 'modules' directory not found")
        
        # Асинхронная загрузка модулей с прогрессом
        for module_file in tqdm(module_files, desc="Загрузка модулей", colour="magenta"):
            plugin_data = self.extract_plugin_metadata(module_file)
            
            # Если плагин пустой (не содержит кода), то его не загружаем
            if plugin_data['active'] == False:
                continue

            try:
                # Импортируем модуль
                module = importlib.import_module(f'modules.{module_file}')
                
                if hasattr(module, 'router'):
                    # Включаем роутер из модуля в dispatcher
                    self.dp.include_routers(module.router)
                    self.logger_service.log_system(f"Модуль {module_file} успешно загружен с роутером.")
                    print(f"modules/{module_file} -> [router]")
                else:
                    self.logger_service.log_system(f"Модуль {module_file} не содержит роутера.")
                    print(f"modules/{module_file} не содержит роутера")
                
                # Сохраняем информацию о плагине в базе данных
                await self.db_service.save_plugin_data(module_file, plugin_data)
            
            except Exception as e:
                # Логирование ошибок и деактивация плагина
                plugin_data['active'] = False
                plugin_data['supported'] = False
                await self.db_service.save_plugin_data(module_file, plugin_data)
                self.logger_service.log_system(f"Ошибка загрузки модуля {module_file}: {e}")
                print(f"Ошибка загрузки модуля {module_file}: {e}")
            
            await asyncio.sleep(0.2)  # Имитируем асинхронную загрузку

        self.logger_service.log_system("Загрузка всех модулей завершена.")

    def extract_plugin_metadata(self, module_file: str):
        """Извлекает метаданные плагина из комментариев в файле модуля."""
        version = None
        author = None
        supported = None
        updates_url = None

        try:
            # Открываем файл плагина для чтения
            with open(f"modules/{module_file}.py", "r", encoding="utf-8") as f:
                content = f.readlines()
            
            # Ищем комментарии с метаданными
            for line in content:
                version_match = re.search(r'#VERSION\s*=\s*(\S+)', line)
                author_match = re.search(r'#AUTHOR\s*=\s*(\S+)', line)
                supported_match = re.search(r'#SUPPORTED\s*=\s*(True|False)', line)
                updates_url_match = re.search(r'#UPDATES_URL\s*=\s*(\S+)', line)

                if version_match:
                    version = version_match.group(1)
                if author_match:
                    author = author_match.group(1)
                if supported_match:
                    supported = supported_match.group(1) == 'True'
                if updates_url_match:
                    updates_url = updates_url_match.group(1)

            # Если плагин не содержит кода, ставим его неактивным
            if not any(line.strip() for line in content):
                return {'active': False, 'supported': False, 'version': None, 'author': None, 'updates_url': None}

            # Если плагин не поддерживается, выключаем его
            if supported is None:
                supported = True  # По умолчанию поддерживается, если не указано

            return {
                'version': version,
                'author': author,
                'supported': supported,
                'updates_url': updates_url,
                'active': True
            }

        except Exception as e:
            self.logger_service.log_system(f"Ошибка при извлечении метаданных из {module_file}: {e}")
            return {'active': False, 'supported': False, 'version': None, 'author': None, 'updates_url': None}
