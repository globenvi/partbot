import json
import os
import aiofiles
import asyncio


class JSONService:
    def __init__(self, data_file_path=None):
        if data_file_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file_path = os.path.join(current_dir, "../datafiles/database.json")

        self.data_file_path = os.path.abspath(data_file_path)  # Приводим к абсолютному пути
        self.data = None  # Данные будут загружены асинхронно

    async def init(self):
        """Асинхронная инициализация данных."""
        self.data = await self.load_data()

    async def load_data(self):
        """Асинхронная загрузка данных из файла JSON"""
        if not os.path.exists(self.data_file_path):
            async with aiofiles.open(self.data_file_path, 'w') as f:
                await f.write(json.dumps({}))  # Создаем пустой JSON объект
        async with aiofiles.open(self.data_file_path, 'r') as f:
            content = await f.read()
            return json.loads(content)

    async def save_data(self):
        """Асинхронное сохранение данных в файл JSON"""
        async with aiofiles.open(self.data_file_path, 'w') as f:
            await f.write(json.dumps(self.data, indent=4))

    async def save_plugin_data(self, module_file, plugin_data):
        """Сохраняет информацию о плагине в базу данных"""
        if self.data is None:
            await self.init()  # Если данные еще не инициализированы, инициализируем их

        if 'plugins' not in self.data:
            self.data['plugins'] = []

        # Проверка на существование плагина с таким же именем
        existing_plugin = await self.find_one('plugins', {'name': module_file})
        if existing_plugin:
            # Обновляем существующий плагин
            await self.update('plugins', existing_plugin['id'], plugin_data)
        else:
            # Добавляем новый плагин
            await self.create('plugins', {'name': module_file, **plugin_data})

        await self.save_data()


    async def create(self, section, record):
        """Асинхронное создание записи в указанном разделе JSON"""
        if section not in self.data:
            self.data[section] = []

        # Проверка на дубликаты по всем полям
        for existing_record in self.data[section]:
            if all(existing_record.get(key) == value for key, value in record.items()):
                return

        # Генерация уникального ID
        record_id = self._generate_id(section)
        record['id'] = record_id

        self.data[section].append(record)
        await self.save_data()

    async def read(self, section):
        """Асинхронное чтение всех записей из указанного раздела JSON"""
        return self.data.get(section, [])

    async def update(self, section, record_id, updated_record):
        """Асинхронное обновление записи по ID в указанном разделе"""
        if section in self.data:
            for idx, record in enumerate(self.data[section]):
                if record['id'] == record_id:
                    self.data[section][idx].update(updated_record)
                    await self.save_data()
                    return

    async def delete(self, section, record_id):
        """Асинхронное удаление записи по ID в указанном разделе"""
        if section in self.data:
            for idx, record in enumerate(self.data[section]):
                if record['id'] == record_id:
                    deleted_record = self.data[section].pop(idx)
                    await self.save_data()
                    return

    async def find_one(self, section, query):
        """Асинхронный поиск одной записи по критериям в указанном разделе"""
        if section in self.data:
            for record in self.data[section]:
                if all(record.get(key) == value for key, value in query.items()):
                    return record
        return None

    async def find_all(self, section, query):
        """Асинхронный поиск всех записей по критериям в указанном разделе"""
        if section in self.data:
            return [record for record in self.data[section] if
                    all(record.get(key) == value for key, value in query.items())]
        return []

    def _generate_id(self, section):
        """Генерация уникального ID для новой записи"""
        if section not in self.data or not self.data[section]:
            return 1
        return max(record['id'] for record in self.data[section]) + 1

    async def test_connection(self):
        """Асинхронное тестирование соединения с файлом JSON"""
        return os.path.exists(self.data_file_path) and os.access(self.data_file_path, os.R_OK | os.W_OK)



# # Пример использования
# if __name__ == "__main__":
#     async def main():
#         db_service = JSONService()
#         await db_service.init()  # Асинхронная инициализация данных

    #     # Тестируем соединение
    #     if await db_service.test_connection():
    #         # Создание записей
    #         await db_service.create('users', {'login': 'user1', 'password': 'pass1', 'email': 'user1@example.com'})
    #         await db_service.create('users', {'login': 'user1', 'password': 'pass2',
    #                                           'email': 'user2@example.com'})  # Дубликат по login и email
    #         await db_service.create('users', {'login': 'user2', 'password': 'pass2', 'email': 'user2@example.com'})  # Новый
    #
    #         # Поиск одной записи
    #         user_record = await db_service.find_one('users', {'login': 'user1'})
    #         print("Найдена запись:", user_record)
    #
    #         # Поиск всех записей с определённым условием
    #         all_users = await db_service.find_all('users', {'password': 'pass2'})
    #         print("Все подходящие записи:", all_users)
    #
    #         # Чтение всех записей
    #         records = await db_service.read('users')
    #         print("Текущие записи в 'users':", records)
    #
    #         # Обновление записи
    #         if records:
    #             await db_service.update('users', records[0]['id'], {'password': 'new_password'})
    #
    #         # Удаление записи
    #         if records:
    #             await db_service.delete('users', records[0]['id'])
    #
    # asyncio.run(main())
