# Room Display - Deployment Guide

## Architecture Overview

```
Browser → nginx (port 443/HTTPS) → gunicorn (port 5000) → Flask (app.py)
```

- **nginx** - Handles HTTPS, routes requests to gunicorn
- **gunicorn** - Runs your Python app reliably
- **systemd** - Keeps gunicorn running, starts on boot
- **Flask** - Your app (reads S3, renders templates)

## Current Server

- Server: varnell.net (134.199.156.90)
- User: jtair
- App location: ~/room_display/

## URLs

- https://varnell.net/room1
- https://varnell.net/room2

---

## Deploying Updates

### Upload changed files (from Mac):
```bash
cd /Users/jtair/Library/CloudStorage/Dropbox/decprograms/docbill/room_display
scp app.py jtair@varnell.net:~/room_display/
scp templates/room.html jtair@varnell.net:~/room_display/templates/
scp -r static/ jtair@varnell.net:~/room_display/
```

### Restart the app:
```bash
ssh jtair@varnell.net
sudo systemctl restart roomdisplay
```

---

## Useful Commands (on server)

```bash
# App status
sudo systemctl status roomdisplay
sudo systemctl restart roomdisplay
sudo systemctl stop roomdisplay

# View logs
journalctl -u roomdisplay -f

# nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t                      # Test config before restart
```

---

## Config File Locations (on server)

```
~/room_display/                    # App files
~/room_display/venv/               # Python virtual environment
/etc/systemd/system/roomdisplay.service   # systemd service
/etc/nginx/sites-available/varnell        # nginx config
```

---

## Fresh Server Setup (for future reference)

### 1. Server setup
```bash
sudo apt update
sudo apt install nginx python3-venv
```

### 2. Upload app files (from Mac)
```bash
ssh user@server "mkdir -p ~/room_display/templates"
scp app.py requirements.txt user@server:~/room_display/
scp templates/room.html user@server:~/room_display/templates/
scp -r static/ user@server:~/room_display/
```

### 3. Python environment
```bash
cd ~/room_display
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Test manually
```bash
source venv/bin/activate
export AWS_ACCESS_KEY_ID='your_key'
export AWS_SECRET_ACCESS_KEY='your_secret'
gunicorn -b 0.0.0.0:5000 app:app
# Visit http://server-ip:5000/room1 to test
# Ctrl+C to stop
```

### 5. Create systemd service
```bash
sudo nano /etc/systemd/system/roomdisplay.service
```

Paste:
```
[Unit]
Description=Room Display Flask App
After=network.target

[Service]
User=jtair
WorkingDirectory=/home/jtair/room_display
Environment="AWS_ACCESS_KEY_ID=your_key"
Environment="AWS_SECRET_ACCESS_KEY=your_secret"
ExecStart=/home/jtair/room_display/venv/bin/gunicorn -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable roomdisplay
sudo systemctl start roomdisplay
```

### 6. Configure nginx
```bash
sudo nano /etc/nginx/sites-available/yourappname
```

Paste (replace `yourappname` and `yourdomain.com` with your values):
```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/yourappname /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Note: On varnell.net, the config file is `/etc/nginx/sites-available/varnell`

### 7. Open firewall (if needed)
```bash
sudo ufw allow 80
sudo ufw allow 443
```

### 8. Add HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Certbot automatically updates your nginx config and restarts nginx. No manual changes needed.

---

## Adding Static Files

1. Upload to `~/static/` on server
2. Edit nginx config to add location block:
   ```
   location /filename.html {
       alias /home/jtair/static/filename.html;
   }
   ```
3. Test and restart: `sudo nginx -t && sudo systemctl restart nginx`
