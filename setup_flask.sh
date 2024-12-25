#!/bin/bash

# Завершение выполнения при ошибках
set -e

# Переменные
DOMAIN="cwim-team.ru"
NGINX_CONFIG="/etc/nginx/sites-available/$DOMAIN"
NGINX_LINK="/etc/nginx/sites-enabled/$DOMAIN"
APP_DIR="/home/$USER/flask_app"
STATIC_DIR="$APP_DIR/static"
SOCK_FILE="$APP_DIR/flask_app.sock"
EMAIL="admin@$DOMAIN"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
    echo "Этот скрипт должен быть запущен с правами root"
    exit 1
fi

# Обновление системы
echo "Обновляем систему..."
apt update && apt upgrade -y

# Установка зависимостей
echo "Устанавливаем зависимости..."
dependencies=(nginx certbot python3-certbot-nginx python3 python3-venv python3-pip curl)
for package in "${dependencies[@]}"; do
    if ! dpkg -l | grep -qw "$package"; then
        echo "Устанавливаем $package..."
        apt install -y "$package"
    else
        echo "$package уже установлен."
    fi
done

# Создание конфигурации Nginx
echo "Создаем конфигурацию Nginx для $DOMAIN..."
cat > "$NGINX_CONFIG" <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://unix:$SOCK_FILE;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $STATIC_DIR/;
    }
}
EOF

# Активируем конфигурацию
ln -sf "$NGINX_CONFIG" "$NGINX_LINK"

# Проверка конфигурации Nginx
echo "Проверяем конфигурацию Nginx..."
if ! nginx -t; then
    echo "Ошибка в конфигурации Nginx. Проверьте конфигурацию: $NGINX_CONFIG"
    exit 1
fi

# Перезапуск Nginx
echo "Перезапускаем Nginx..."
systemctl restart nginx || {
    echo "Не удалось перезапустить Nginx. Проверьте статус с помощью: systemctl status nginx"
    exit 1
}

# Проверка наличия SSL-сертификатов
if [ -d "$CERT_PATH" ]; then
    echo "SSL-сертификаты для $DOMAIN уже существуют. Пропускаем Certbot."
else
    echo "Запрашиваем SSL-сертификаты у Let's Encrypt..."
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL || {
        echo "Certbot завершился ошибкой. Проверьте логи: /var/log/letsencrypt/letsencrypt.log"
        exit 1
    }
fi

# Установка и запуск Flask-приложения (если нужно)
if [[ -f "$APP_DIR/app.py" ]]; then
    echo "Настраиваем и запускаем Flask-приложение..."
    cd "$APP_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    gunicorn --bind unix:"$SOCK_FILE" -m 007 app:app --daemon
    echo "Flask-приложение запущено и работает через Gunicorn."
else
    echo "Flask-приложение не найдено в $APP_DIR. Пропускаем настройку приложения."
fi

# Финальное сообщение
echo "Настройка завершена! Домен $DOMAIN настроен с поддержкой SSL."
echo "Если возникли проблемы, проверьте логи: /var/log/nginx/error.log и /var/log/letsencrypt/letsencrypt.log"
