import os

def check_licenses():
    # Проверка наличия лицензионного файла или соответствующих файлов
    license_file_path = 'LICENSE'
    if not os.path.exists(license_file_path):
        print(f"Warning: {license_file_path} not found! Make sure to include a license.")
        return False
    else:
        print(f"License check passed: {license_file_path} found.")
        return True
