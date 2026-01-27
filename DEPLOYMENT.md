# RSU Library — Deployment Guide (Ubuntu 22.04 LTS)

This guide explains how to deploy the RSU Library (Django) project on **Ubuntu 22.04 LTS** using Docker and Docker Compose, and how to expose it via Nginx.

---

## 1. Prerequisites

- Ubuntu 22.04 LTS server with SSH access
- Sudo privileges

---

## 2. Install Docker on Ubuntu 22.04

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker dependencies
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key and repository
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# (Optional) Run Docker without sudo
sudo usermod -aG docker $USER
# Log out and back in (or run: newgrp docker) for this to take effect

# Verify
docker --version
docker compose version
```

---

## 3. Install Docker Compose (standalone, if not using the plugin)

If you prefer the standalone `docker-compose` binary:

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

> **Note:** This project uses `docker compose` (plugin). If you use standalone, replace `docker compose` with `docker-compose` in the commands below.

---

## 4. Clone the Repository and Set Environment Variables

```bash
# Clone (replace with your repo URL)
git clone https://github.com/your-org/rsu_project.git
cd rsu_project

# Create a production .env (optional; docker-compose also supports env in the file)
cp .env.example .env 2>/dev/null || true

# Edit .env with your values (or set in docker-compose.yml)
nano .env
```

**Example `.env` for production:**

```env
DJANGO_SECRET_KEY=your-long-random-secret-key-here
DJANGO_DEBUG=False
DB_NAME=rsu_db
DB_USER=rsu_user
DB_PASSWORD=your-strong-db-password
DB_HOST=db
DB_PORT=5432
# If behind Nginx with HTTPS:
# CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

To load `.env` in Docker Compose, add to `docker-compose.yml` under the `web` service:

```yaml
env_file:
  - .env
```

Or set variables in the `environment:` section (as in the current `docker-compose.yml`).

---

## 5. Build and Run the Containers

```bash
# Build and start in detached mode
docker compose build
docker compose up -d

# If you see DB connection errors on first run (Postgres not ready), wait a few seconds and:
docker compose up -d
```

**Useful commands:**

```bash
# View logs
docker compose logs -f web

# Restart after code/config changes
docker compose build --no-cache web && docker compose up -d

# Stop
docker compose down

# Stop and remove volumes (deletes DB and uploaded files)
docker compose down -v
```

---

## 6. Access the Application Locally

- **On the server:**  
  - HTTP: `http://localhost:8080` or `http://127.0.0.1:8080`  
- **From another machine on the same network:**  
  - `http://<server-ip>:8080`

**Default root user (created by `create_root_user`):**

- Username: `zero`  
- Password: `975312468qq`  

Change this in production (e.g. via Django admin or a dedicated management command).

---

## 7. Expose the Application to the Internet (Nginx Reverse Proxy)

### 7.1 Install Nginx

```bash
sudo apt install -y nginx
```

### 7.2 Create an Nginx Site Configuration

```bash
sudo nano /etc/nginx/sites-available/rsu-library
```

**HTTP only (for testing):**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 150M;

    location /static/ {
        alias /var/www/rsu-library/staticfiles/;
    }

    location /media/ {
        alias /var/www/rsu-library/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**HTTPS with Let’s Encrypt (recommended for production):**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    # Optional: include /etc/letsencrypt/options-ssl-nginx.conf; ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 150M;

    location /static/ {
        alias /var/www/rsu-library/staticfiles/;
    }

    location /media/ {
        alias /var/www/rsu-library/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Replace `yourdomain.com` with your domain.

### 7.3 Static and Media Files When Using Nginx

The app serves `/static/` and `/media/` from inside the container. To serve them from the host (better for Nginx), you can bind those directories.

**Option A – Use existing Docker volumes and copy from container (one-time after deploy):**

```bash
# Create dirs on host
sudo mkdir -p /var/www/rsu-library/staticfiles /var/www/rsu-library/media

# Copy from container (run once after first successful `up`)
docker compose run --rm web python manage.py collectstatic --noinput
# For media: if you use a bind mount for media, ensure the app writes to that path;  
# otherwise copy from the volume (e.g. use a temporary container that mounts the volume).
```

**Option B – Bind host directories in `docker-compose.yml`:**

Under the `web` service, replace or add volume mounts so Nginx can read from the host:

```yaml
volumes:
  - .:/app
  - /var/www/rsu-library/staticfiles:/app/staticfiles
  - /var/www/rsu-library/media:/app/media
```

Then run:

```bash
sudo mkdir -p /var/www/rsu-library/staticfiles /var/www/rsu-library/media
sudo chown -R $USER:$USER /var/www/rsu-library
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d
```

Point Nginx `alias` to `/var/www/rsu-library/staticfiles/` and `/var/www/rsu-library/media/` as in the examples above.

### 7.4 Enable the Site and Reload Nginx

```bash
sudo ln -s /etc/nginx/sites-available/rsu-library /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7.5 HTTPS with Certbot (Let’s Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

If you use the HTTPS Nginx config, set in `.env` (or in `docker-compose` `environment`):

```env
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

Then:

```bash
docker compose up -d --force-recreate
```

---

## 8. Firewall (Optional)

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
# If you need direct access to the app during setup: sudo ufw allow 8080/tcp
sudo ufw enable
sudo ufw status
```

---

## 9. Quick Reference

| Task                 | Command / URL                                      |
|----------------------|----------------------------------------------------|
| Local app (on host)  | `http://localhost:8080`                            |
| Logs                 | `docker compose logs -f web`                       |
| Rebuild and start    | `docker compose build && docker compose up -d`     |
| Stop                 | `docker compose down`                              |
| Root login           | `zero` / `975312468qq` (change in production)      |

---

## 10. Troubleshooting

- **“Connection refused” to DB on first `up`:**  
  Postgres may not be ready. Run `docker compose up -d` again after a few seconds.

- **502 Bad Gateway from Nginx:**  
  - Check that the app is listening: `docker compose ps` and `docker compose logs web`.  
  - Ensure `proxy_pass` uses the same port as in `docker-compose.yml` (e.g. `8080:8000` → `http://127.0.0.1:8080`).

- **CSRF or “Forbidden” on login when using HTTPS:**  
  - Set `CSRF_TRUSTED_ORIGINS` to your `https://` domain(s) and restart the `web` container.

- **Static/Media 404:**  
  - Run `collectstatic` and ensure Nginx `alias` paths exist and match the `STATIC_ROOT` / `MEDIA_ROOT` (or the bind-mounted paths).

- **Login fails with valid credentials:**  
  - Ensure `create_root_user` has run (check `docker compose logs web` for “Root user 'zero' created”).  
  - Confirm `LOGIN_REDIRECT_URL` is `home` (not `login`) and that DB env vars match the `db` service.
