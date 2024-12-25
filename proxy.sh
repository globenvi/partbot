#!/bin/bash

# Обновление и установка необходимых пакетов
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y nginx certbot python3-certbot-nginx openssl

# Настройка Nginx для проксирования
NGINX_CONF="/etc/nginx/sites-available/cwim-team.ru"
NGINX_LINK="/etc/nginx/sites-enabled/cwim-team.ru"
SSL_DIR="/etc/nginx/ssl"

echo "Создаём конфигурацию Nginx для cwim-team.ru..."
sudo mkdir -p $SSL_DIR

# Создание временного SSL-сертификата, если Let's Encrypt недоступен
if [ ! -f "$SSL_DIR/temporary.crt" ]; then
    echo "Создаём временный SSL-сертификат..."
    sudo openssl req -x509 -nodes -days 90 -newkey rsa:2048 \
        -keyout "$SSL_DIR/temporary.key" \
        -out "$SSL_DIR/temporary.crt" \
        -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=cwim-team.ru"
fi

# Создаём конфигурацию Nginx
sudo bash -c "cat > $NGINX_CONF" <<EOL
server {
    listen 80;
    server_name cwim-team.ru www.cwim-team.ru;

    location / {
        proxy_pass http://127.0.0.1:80; # Локальный Flask-сервер
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Redirect HTTP to HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name cwim-team.ru www.cwim-team.ru;

    ssl_certificate $SSL_DIR/temporary.crt;
    ssl_certificate_key $SSL_DIR/temporary.key;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Удаление дефолтного конфигурационного файла (если существует)
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    echo "Удаляем дефолтный конфиг Nginx..."
    sudo rm /etc/nginx/sites-enabled/default
fi

# Включение нового конфигурационного файла
if [ ! -f "$NGINX_LINK" ]; then
    echo "Включаем конфигурацию cwim-team.ru..."
    sudo ln -s $NGINX_CONF $NGINX_LINK
fi

# Перезапуск Nginx
echo "Перезапускаем Nginx..."
sudo nginx -t && sudo systemctl restart nginx

# Проверка наличия SSL-сертификата от Let's Encrypt
if ! sudo certbot certificates | grep -q "Domains: cwim-team.ru"; then
    echo "SSL-сертификат от Let's Encrypt не найден. Создаём сертификат..."
    sudo certbot --nginx -d cwim-team.ru -d www.cwim-team.ru --non-interactive --agree-tos -m admin@cwim-team.ru || echo "Не удалось получить сертификат от Let's Encrypt."
fi

# Убедиться, что Nginx запущен с корректной конфигурацией
echo "Перезапускаем Nginx для применения настроек HTTPS..."
sudo nginx -t && sudo systemctl restart nginx

echo "Настройка завершена. Домен cwim-team.ru настроен для работы через HTTPS."
