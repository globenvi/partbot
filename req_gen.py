import subprocess

def generate_requirements_txt(filename='requirements.txt'):
    try:
        # Запуск команды pip freeze для получения списка установленных пакетов
        result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, text=True, check=True)

        # Запись результатов в файл
        with open(filename, 'w') as f:
            f.write(result.stdout)

        print(f"Файл {filename} успешно создан!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при генерации requirements.txt: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    generate_requirements_txt()
