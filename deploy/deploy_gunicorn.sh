#!/usr/bin/env bash
set -euo pipefail
# Simple deploy helper (run on the target server). Review before running.

REPO_DIR=/opt/sam_blocks_inventory
SERVICE_NAME=sam_blocks.service

echo "Deploy helper — clone/update repo, create venv, install deps, init DB, install systemd/nginx configs"

if [ ! -d "$REPO_DIR" ]; then
  echo "Cloning repo to $REPO_DIR"
  sudo git clone https://github.com/Teejay2223/sam-blocks-and-interlocks-inventory.git "$REPO_DIR"
  sudo chown -R $(id -u):$(id -g) "$REPO_DIR"
fi

cd "$REPO_DIR"
echo "Pulling latest..."
git pull --rebase

echo "Creating python venv and installing requirements"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing DB (FORCE_SQLITE=1)"
export FORCE_SQLITE=1
flask --app app init-db

echo "Installing systemd unit and nginx site (requires sudo)"
sudo cp deploy/sam_blocks.service /etc/systemd/system/$SERVICE_NAME
sudo cp deploy/nginx_sam_blocks.conf /etc/nginx/sites-available/sam_blocks
sudo ln -sf /etc/nginx/sites-available/sam_blocks /etc/nginx/sites-enabled/sam_blocks

echo "Reloading systemd and starting service"
sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICE_NAME

echo "Testing nginx config and restarting nginx"
sudo nginx -t
sudo systemctl restart nginx

echo "Deployed. Visit http://<server-ip>/"
