#!/bin/bash

# Exit on errors
set -e

# Variables
DOMAIN="cwim-team.ru"
NGINX_CONFIG="/etc/nginx/sites-available/$DOMAIN"
NGINX_LINK="/etc/nginx/sites-enabled/$DOMAIN"
APP_DIR="/home/$USER/flask_app"
STATIC_DIR="$APP_DIR/static"
SOCK_FILE="$APP_DIR/flask_app.sock"

# Check for sudo/root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Update system
apt update && apt upgrade -y

# Install dependencies if not present
apt install -y nginx certbot python3-certbot-nginx

# Create Nginx configuration file
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

    listen 80;
}
EOF

# Enable Nginx site and restart Nginx
ln -sf "$NGINX_CONFIG" "$NGINX_LINK"
nginx -t
systemctl restart nginx

# Configure SSL using Certbot
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

# Final message
echo "Nginx configured for $DOMAIN with SSL."
