Deploy: Gunicorn + systemd + Nginx
=================================

This folder contains templates and a helper script to deploy the app on a Linux server (Ubuntu/Debian-style).

Files
- `sam_blocks.service` — systemd unit file. Copy to `/etc/systemd/system/sam_blocks.service` and `systemctl daemon-reload`.
- `nginx_sam_blocks.conf` — example nginx site config. Copy to `/etc/nginx/sites-available/sam_blocks` and symlink to `sites-enabled`.
- `deploy_gunicorn.sh` — convenience script to clone/pull the repo, create a venv, install deps, init the DB (FORCE_SQLITE), and install the templates. Review before running.

Quick manual steps (summary)
1. On the server, install required packages:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx
```

2. Clone repo and set up venv (the script automates this):

```bash
sudo mkdir -p /opt/sam_blocks_inventory
sudo chown $USER:$USER /opt/sam_blocks_inventory
git clone https://github.com/Teejay2223/sam-blocks-and-interlocks-inventory.git /opt/sam_blocks_inventory
cd /opt/sam_blocks_inventory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Initialize DB (example uses SQLite):

```bash
export FORCE_SQLITE=1
flask --app app init-db
```

4. Install systemd unit and nginx config (requires sudo):

```bash
sudo cp deploy/sam_blocks.service /etc/systemd/system/
sudo cp deploy/nginx_sam_blocks.conf /etc/nginx/sites-available/sam_blocks
sudo ln -s /etc/nginx/sites-available/sam_blocks /etc/nginx/sites-enabled/
sudo systemctl daemon-reload
sudo systemctl enable --now sam_blocks.service
sudo nginx -t
sudo systemctl restart nginx
```

Notes
- The systemd unit uses `/opt/sam_blocks_inventory` as WorkingDirectory and defaults `FORCE_SQLITE=1` for a safe quick deployment. Remove that env line to use `DATABASE_URL` for Postgres.
- Ensure the `www-data` user can access the repo files (chown accordingly). Alternatively change `User` in the unit.
- For production, consider using a managed Postgres instance and setting `DATABASE_URL` (and running the migration script) instead of SQLite.
