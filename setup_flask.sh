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
AVAILABLE_PORT=""

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root" 
   exit 1
fi

# Обновление системы
apt update && apt upgrade -y

# Установка зависимостей, если их нет
dependencies=(nginx certbot python3-certbot-nginx python3 python3-venv python3-pip curl)
for package in "${dependencies[@]}"; do
    if ! dpkg -l | grep -qw "$package"; then
        echo "Устанавливаем $package..."
        apt install -y "$package"
    else
        echo "$package уже установлен."
    fi
done

# Проверка портов 80 и 443
for port in 80 443; do
    if ! ss -tuln | grep -q ":$port"; then
        echo "Порт $port свободен."
        AVAILABLE_PORT=$port
        break
    else
        echo "Порт $port занят."
    fi
done

# Если порты 80 и 443 заняты, используем порт 8080
if [[ -z "$AVAILABLE_PORT" ]]; then
    echo "Порты 80 и 443 заняты, переключаемся на порт 8080."
    AVAILABLE_PORT=8080
fi

# Проверка доступности домена
if ! curl -s --head "http://$DOMAIN" | grep "200 OK"; then
    echo "Домен $DOMAIN недоступен. Проверьте настройки DNS и правила брандмауэра."
    exit 1
fi

# Создание конфигурационного файла Nginx
cat > "$NGINX_CONFIG" <<EOF
server {
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

    listen $AVAILABLE_PORT;
}
EOF

# Включение сайта в Nginx и перезапуск
ln -sf "$NGINX_CONFIG" "$NGINX_LINK"
nginx -t || {
    echo "Тест конфигурации Nginx завершился ошибкой. Исправьте ошибки и перезапустите скрипт."
    exit 1
}
systemctl restart nginx || {
    echo "Не удалось перезапустить Nginx. Проверьте статус с помощью: systemctl status nginx"
    exit 1
}

# Проверка наличия SSL-сертификатов
if [ -d "$CERT_PATH" ]; then
    echo "SSL-сертификаты для $DOMAIN уже существуют. Пропускаем Certbot."
else
    echo "SSL-сертификаты не найдены. Запрашиваю сертификаты у Let's Encrypt..."
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL || {
        echo "Certbot завершился ошибкой. Возможные причины:"
        echo "1. Настройки DNS: Убедитесь, что $DOMAIN указывает на IP вашего сервера."
        echo "2. Брандмауэр: Откройте порты 80 и 443."
        echo "3. Логи: /var/log/letsencrypt/letsencrypt.log"
        exit 1
    }
fi

# Финальное сообщение
echo "Nginx настроен для $DOMAIN с SSL."
echo "Если возникли проблемы, проверьте: /var/log/nginx/error.log и /var/log/letsencrypt/letsencrypt.log"
