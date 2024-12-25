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
EMAIL="admin@$DOMAIN"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

# Check for sudo/root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Update system
apt update && apt upgrade -y

# Install dependencies if not present
dependencies=(nginx certbot python3-certbot-nginx python3 python3-venv python3-pip)
for package in "${dependencies[@]}"; do
    if ! dpkg -l | grep -qw "$package"; then
        echo "Installing $package..."
        apt install -y "$package"
    else
        echo "$package is already installed."
    fi
done

# Check for open ports 80 and 443
for port in 80 443; do
    if ! ss -tuln | grep -q ":$port"; then
        echo "Port $port is free."
    else
        echo "Warning: Port $port is in use. Ensure no conflicting services are running."
    fi
done

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
nginx -t || {
    echo "Nginx configuration test failed. Fix the issues and re-run the script."
    exit 1
}
systemctl restart nginx || {
    echo "Restarting Nginx failed. Check the status with: systemctl status nginx"
    exit 1
}

# Check for existing SSL certificates
if [ -d "$CERT_PATH" ]; then
    echo "SSL certificates already exist for $DOMAIN. Skipping Certbot."
else
    echo "SSL certificates not found. Requesting certificates from Let's Encrypt..."
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL || {
        echo "Certbot failed. Check DNS settings or firewall rules."
        echo "Ensure the domain points to this server and ports 80/443 are open."
        exit 1
    }
fi

# Final message
echo "Nginx configured for $DOMAIN with SSL."
echo "If there are issues, check: /var/log/nginx/error.log and /var/log/letsencrypt/letsencrypt.log"
