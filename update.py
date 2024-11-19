import os
import shutil
import subprocess
import requests
import time
from zipfile import ZipFile

# Конфигурация
GITHUB_REPO = "globenvi/partbot"  # Репозиторий
BRANCH = "main"  # Ветка
CHECK_INTERVAL = 10  # Интервал проверки обновлений в секундах
LAST_COMMIT_FILE = "last_commit.txt"  # Файл для хранения последнего зафиксированного коммита

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
        # Перемещаем файлы на текущий уровень
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

def run_main_script():
    """Запускает __main__.py в новом процессе."""
    try:
        print(f"Перезапуск __main__.py...")
        return subprocess.Popen(["python3", "__main__.py"])
    except Exception as e:
        print(f"Ошибка при перезапуске __main__.py: {e}")
        raise

def terminate_process(process):
    """Корректно завершает процесс."""
    if process and process.poll() is None:  # Проверяем, активен ли процесс
        print("Завершаем предыдущий процесс...")
        process.terminate()
        process.wait()  # Ждем завершения процесса
        print("Процесс успешно завершен.")

def main():
    """Основная логика."""
    main_process = None
    is_first_run = not os.path.exists(LAST_COMMIT_FILE)

    while True:
        try:
            latest_commit = get_latest_commit(GITHUB_REPO, BRANCH)
            if os.path.exists(LAST_COMMIT_FILE):
                with open(LAST_COMMIT_FILE, "r") as f:
                    last_commit = f.read().strip()
            else:
                last_commit = None

            if is_first_run or latest_commit != last_commit:
                if is_first_run:
                    print("Первичный запуск: обновляем проект.")
                else:
                    print(f"Найдены обновления: {latest_commit}")

                download_repository(GITHUB_REPO, BRANCH)
                extract_and_replace("repo.zip", ".")
                install_requirements()
                with open(LAST_COMMIT_FILE, "w") as f:
                    f.write(latest_commit)

                # Перезапуск основного скрипта
                terminate_process(main_process)  # Завершаем старый процесс
                main_process = run_main_script()

                is_first_run = False
            else:
                print("Обновлений не найдено.")
        except Exception as e:
            print(f"Ошибка: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
