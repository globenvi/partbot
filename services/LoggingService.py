import os
import logging
from datetime import datetime

class LoggerService:
    def __init__(self):
        self.logs_path = os.path.join(os.getcwd(), "logs")
        self.create_logs_folder()
        self.main_log_file = self.create_log_file("system")
        self.bot_log_file = self.create_log_file("bot")

        # Настройка основного логгера
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.main_log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger()

    def create_logs_folder(self):
        """Создает папку logs/ если она отсутствует."""
        os.makedirs(self.logs_path, exist_ok=True)

    def create_log_file(self, log_name: str) -> str:
        """Создает файл лога с уникальным именем."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(self.logs_path, f"{log_name}_{timestamp}.log")
        return log_file

    def log_system(self, message: str, level="info"):
        """Логгирование системных событий."""
        getattr(self.logger, level)(message)

    def log_bot_activity(self, message: str):
        """Логгирование событий, связанных с ботом."""
        with open(self.bot_log_file, 'a') as bot_log:
            bot_log.write(f"[{datetime.now()}] {message}\n")
