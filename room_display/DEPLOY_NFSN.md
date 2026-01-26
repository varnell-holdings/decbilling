# Room Display - NearlyFreeSpeech.net Deployment Guide

## Architecture Overview

```
Browser → NFSN Proxy → gunicorn (port 8000) → Flask (app.py)
```

- **NFSN Proxy** - Routes requests to your app (replaces nginx)
- **Daemon** - NFSN's way to run background processes (replaces systemd)
- **gunicorn** - Runs your Python app
- **Flask** - Your app (reads S3, renders templates)

## Current Server

- Server: dec601.nfshost.com
- SSH: `ssh jtillett_dec601@ssh.nyc1.nearlyfreespeech.net`
- App location: `/home/protected/roomdisplay/`
- Static files: `/home/protected/roomdisplay/static/`

## URLs

- https://dec601.nfshost.com/room1
- https://dec601.nfshost.com/room2
- https://dec601.nfshost.com/deccal.html

---

## Deploying Updates

### Upload changed files (from Mac):
```bash
cd /Users/jtair/Library/CloudStorage/Dropbox/decprograms/docbill/room_display
scp app.py jtillett_dec601@ssh.nyc1.nearlyfreespeech.net:/home/protected/roomdisplay/
scp templates/room.html jtillett_dec601@ssh.nyc1.nearlyfreespeech.net:/home/protected/roomdisplay/templates/
scp -r static/ jtillett_dec601@ssh.nyc1.nearlyfreespeech.net:/home/protected/roomdisplay/
```

### Restart the app:
Go to NFSN control panel → Sites → dec601 → Daemon section → Stop, then Start

Or check logs:
```bash
ssh jtillett_dec601@ssh.nyc1.nearlyfreespeech.net
cat /home/logs/daemon_roomdisplay.log
```

---

## File Locations (on server)

```
/home/protected/roomdisplay/           # App files
/home/protected/roomdisplay/app.py     # Flask application
/home/protected/roomdisplay/templates/ # HTML templates
/home/protected/roomdisplay/static/    # Favicons, static files (deccal.html)
/home/protected/roomdisplay/venv/      # Python virtual environment
/home/protected/roomdisplay/run.sh     # Startup script
/home/logs/daemon_roomdisplay.log      # Daemon logs
```

---

## Key Configuration

### run.sh (startup script)
```bash
#!/bin/sh
. /home/protected/roomdisplay/venv/bin/activate
export AWS_ACCESS_KEY_ID='your_key'
export AWS_SECRET_ACCESS_KEY='your_secret'
exec gunicorn --bind 0.0.0.0:8000 app:app
```

### NFSN Control Panel Settings

**Daemon:**
- Tag: `roomdisplay`
- Command Line: `/home/protected/roomdisplay/run.sh`
- Working Directory: `/home/protected/roomdisplay`
- Run Daemon as: `web`

**Proxy:**
- Protocol: `HTTP`
- Base URI: `/`
- Document Root: `/`
- Target Port: `8000`

---

## Fresh Server Setup (for future reference)

### Prerequisites
- NFSN site type: "Custom" or "Apache 2.4 Generic" (must support Daemon and Proxy)
- Python 3 available on server

### 1. Create project folder
```bash
ssh user@ssh.nyc1.nearlyfreespeech.net
mkdir -p /home/protected/roomdisplay
cd /home/protected/roomdisplay
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install flask gunicorn boto3
```

### 3. Upload app files (from Mac)
```bash
scp app.py user@ssh.nyc1.nearlyfreespeech.net:/home/protected/roomdisplay/
scp -r templates/ user@ssh.nyc1.nearlyfreespeech.net:/home/protected/roomdisplay/
scp -r static/ user@ssh.nyc1.nearlyfreespeech.net:/home/protected/roomdisplay/
```

### 4. Create startup script
```bash
ssh user@ssh.nyc1.nearlyfreespeech.net
cd /home/protected/roomdisplay
nano run.sh
```

Paste:
```bash
#!/bin/sh
. /home/protected/roomdisplay/venv/bin/activate
export AWS_ACCESS_KEY_ID='your_key'
export AWS_SECRET_ACCESS_KEY='your_secret'
exec gunicorn --bind 0.0.0.0:8000 app:app
```

Make executable:
```bash
chmod +x run.sh
```

### 5. Configure NFSN control panel

**Add Daemon:**
- Tag: `roomdisplay`
- Command Line: `/home/protected/roomdisplay/run.sh`
- Working Directory: `/home/protected/roomdisplay`
- Run Daemon as: `web`

**Add Proxy:**
- Protocol: `HTTP`
- Base URI: `/`
- Document Root: `/`
- Target Port: `8000`

### 6. Start the daemon
Click "Start" in the Daemon section of the control panel.

### 7. Check logs if issues
```bash
cat /home/logs/daemon_roomdisplay.log
```

---

## Adding Static Files

Since the proxy routes all requests to Flask, static files must be served by Flask.

1. Upload file to `/home/protected/roomdisplay/static/`
2. Add a route in app.py:
   ```python
   @app.route('/filename.html')
   def filename():
       return send_from_directory('static', 'filename.html')
   ```
3. Upload updated app.py and restart daemon

---

## Differences from Digital Ocean

| Feature | Digital Ocean | NFSN |
|---------|--------------|------|
| Web server | nginx (you configure) | NFSN Proxy (control panel) |
| Process manager | systemd | NFSN Daemon (control panel) |
| Config files | /etc/nginx/, /etc/systemd/ | run.sh + control panel |
| Restart app | `sudo systemctl restart` | Control panel Stop/Start |
| Logs | `journalctl -u roomdisplay` | `/home/logs/daemon_*.log` |
| SSL/HTTPS | Let's Encrypt + certbot | Automatic (NFSN handles it) |

---

## Troubleshooting

**Daemon won't start:**
- Check `/home/logs/daemon_roomdisplay.log` for errors
- Verify working directory is `/home/protected/roomdisplay` (not `/home/public/`)
- Verify run.sh is executable (`chmod +x run.sh`)

**Wrong date showing:**
- Server is in UTC; app uses `ZoneInfo('Australia/Sydney')` to convert

**Static files not loading:**
- With Base URI `/`, all requests go to Flask
- Static files need routes in app.py or must be in Flask's static folder
