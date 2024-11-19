import os
import shutil
import subprocess
import requests
import time
import json
from zipfile import ZipFile

# Конфигурация
GITHUB_REPO = "globenvi/partbot"  # Репозиторий
BRANCH = "main"  # Ветка
CHECK_INTERVAL = 10  # Интервал проверки обновлений в секундах
LAST_COMMIT_FILE = "last_commit.txt"  # Файл для хранения последнего зафиксированного коммита
CONFIG_FILE = "config.json"  # Файл конфигурации
ENV_FILE = ".env"  # Файл .env

def get_latest_commit(repo, branch):
    """Получает последний коммит из GitHub."""
    url = f"https://api.github.com/repos/{repo}/commits/{branch}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["sha"]

def download_repository(repo, branch, dest="repo.zip"):
    """Скачивает ZIP-архив репозитория."""
    url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Репозиторий скачан: {dest}")
    except requests.RequestException as e:
        print(f"Ошибка при скачивании репозитория: {e}")
        raise

def extract_and_replace(zip_path, target_dir):
    """Извлекает файлы из ZIP-архива и заменяет текущие файлы."""
    try:
        with ZipFile(zip_path, 'r') as zip_ref:
            extracted_dir = zip_ref.namelist()[0]  # Первая папка из архива
            zip_ref.extractall(target_dir)
        extracted_path = os.path.join(target_dir, extracted_dir)
        for item in os.listdir(extracted_path):
            s = os.path.join(extracted_path, item)
            d = os.path.join(target_dir, item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            shutil.move(s, d)
        shutil.rmtree(extracted_path)  # Удаляем временную папку
        os.remove(zip_path)  # Удаляем архив
        print("Обновление файлов завершено.")
    except Exception as e:
        print(f"Ошибка при извлечении и замене файлов: {e}")
        raise

def install_requirements():
    """Устанавливает зависимости из requirements.txt, если файл существует."""
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        try:
            print("Установка зависимостей из requirements.txt...")
            subprocess.check_call(["python3", "-m", "pip", "install", "-r", req_file])
            print("Зависимости успешно установлены.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при установке зависимостей: {e}")
            raise
    else:
        print("Файл requirements.txt не найден, пропускаем установку зависимостей.")

def create_config():
    """Создает config.json, если он отсутствует."""
    if not os.path.exists(CONFIG_FILE):
        print("Файл config.json не найден. Запрашиваю параметры для создания...")
        admin_id = input("Введите Telegram ID администратора: ")
        db_type = input("Выберите тип базы данных (local/mongo/mysql/postgresql): ").strip().lower()
        db_config = {}

        if db_type == "local":
            db_config = {"type": "local", "path": "database.json"}
        elif db_type in ["mongo", "mysql", "postgresql"]:
            db_config["type"] = db_type
            db_config["host"] = input(f"Введите хост для {db_type}: ")
            db_config["port"] = input(f"Введите порт для {db_type}: ")
            db_config["user"] = input(f"Введите пользователя для {db_type}: ")
            db_config["password"] = input(f"Введите пароль для {db_type}: ")
            db_config["database"] = input(f"Введите имя базы данных для {db_type}: ")
        else:
            raise ValueError("Недопустимый тип базы данных!")

        update_mode = input("Выберите режим обновлений (auto/manual): ").strip().lower()
        if update_mode not in ["auto", "manual"]:
            raise ValueError("Недопустимый режим обновлений!")

        config = {
            "admin_id": admin_id,
            "database": db_config,
            "update_mode": update_mode
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("Файл config.json успешно создан.")

def create_env():
    """Создает .env, если он отсутствует."""
    if not os.path.exists(ENV_FILE):
        print("Файл .env не найден. Создаю новый...")
        bot_token = input("Введите BOT_TOKEN: ")
        with open(ENV_FILE, "w") as f:
            f.write(f"BOT_TOKEN={bot_token}\n")
        print("Файл .env успешно создан.")

def run_main_script():
    """Запускает __main__.py в новом процессе."""
    try:
        print("Перезапуск __main__.py...")
        return subprocess.Popen(["python3", "__main__.py"])
    except Exception as e:
        print(f"Ошибка при перезапуске __main__.py: {e}")
        raise

def terminate_process(process):
    """Корректно завершает процесс."""
    if process and process.poll() is None:  # Проверяем, активен ли процесс
        print("Завершаем предыдущий процесс...")
        process.terminate()
        process.wait()
        print("Процесс успешно завершен.")

def manual_update():
    """Ручное обновление."""
    print("Ручное обновление запущено...")
    latest_commit = get_latest_commit(GITHUB_REPO, BRANCH)
    with open(LAST_COMMIT_FILE, "r") as f:
        last_commit = f.read().strip()
    if latest_commit != last_commit:
        download_repository(GITHUB_REPO, BRANCH)
        extract_and_replace("repo.zip", ".")
        install_requirements()
        with open(LAST_COMMIT_FILE, "w") as f:
            f.write(latest_commit)
        print("Ручное обновление завершено.")
    else:
        print("Обновлений нет.")

def main():
    """Основная логика."""
    create_config()
    create_env()
    main_process = None
    is_first_run = not os.path.exists(LAST_COMMIT_FILE)

    while True:
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
            update_mode = config.get("update_mode", "manual")

            latest_commit = get_latest_commit(GITHUB_REPO, BRANCH)
            if os.path.exists(LAST_COMMIT_FILE):
                with open(LAST_COMMIT_FILE, "r") as f:
                    last_commit = f.read().strip()
            else:
                last_commit = None

            if is_first_run or latest_commit != last_commit:
                if update_mode == "auto":
                    download_repository(GITHUB_REPO, BRANCH)
                    extract_and_replace("repo.zip", ".")
                    install_requirements()
                    with open(LAST_COMMIT_FILE, "w") as f:
                        f.write(latest_commit)
                    terminate_process(main_process)
                    main_process = run_main_script()
                    is_first_run = False
                else:
                    print("Обновления доступны. Запустите команду для ручного обновления.")
            else:
                print("Обновлений не найдено.")
        except Exception as e:
            print(f"Ошибка: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
