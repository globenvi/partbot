import os
import subprocess
from environs import Env

class WebViewService:
    def __init__(self):
        env = Env()
        env.read_env()  # Чтение .env файла

        # Путь к папке и файлу приложения
        self.web_path = os.path.join(os.getcwd(), "web")
        self.app_file = os.path.join(self.web_path, "app.py")

        self.flask_process = None

    def start_server(self):
        """Запускает Flask сервер через subprocess."""
        flask_command = [
            "python",  # Запуск Python
            self.app_file  # Путь к Flask приложению
        ]
        env = os.environ.copy()
        self.flask_process = subprocess.Popen(flask_command, env=env)

    def start(self):
        """Запускает Flask сервер."""
        self.start_server()

    def stop(self):
        """Останавливает Flask сервер."""
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process.wait()
            print("Flask server stopped.")

if __name__ == "__main__":
    try:
        webview = WebViewService()
        webview.start()
        input("Press Enter to stop the server...")
    finally:
        webview.stop()
