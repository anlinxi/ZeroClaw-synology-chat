# ZeroClaw-SynologyChat Relay Service
A **ZeroClaw ↔ Synology Chat bidirectional message relay service** developed with Flask, 100% compatible with Synology Chat official API specifications. It completely resolves issues like message format errors, long message truncation, missing target users, and interface errors. Ready to use out of the box.

---

## 🌟 Features
1. **Bidirectional Message Communication**: Seamless integration between Synology Chat and ZeroClaw AI for sending and receiving messages
2. **Automatic Long Message Segmentation**: Breaks through Synology's message length limit, automatically splitting and sending in multiple segments
3. **Official Format Compatibility**: Replicates OpenClaw official plugin format, no 120/800/104 errors
4. **Interface Rate Limiting Protection**: 500ms sending interval to avoid Synology interface rate limiting
5. **Security Token Verification**: Validates request legitimacy and rejects unauthorized calls
6. **Comprehensive Console Logging**: Full-process log output for easy troubleshooting

---

## 📋 Requirements
- Linux server (Debian/Ubuntu/CentOS)
- Python 3.7 or higher
- ZeroClaw service already deployed
- Synology NAS + Synology Chat app installed

---

## 🛠️ Installation Steps
### 1. Upload Code
Upload the project file `main.py` to the server directory, example path:
```
/www/wwwroot/pythonProject/zeroClawChatService/
```

### 2. Install Python Dependencies
Enter the project directory and execute the dependency installation command:
```bash
pip install flask requests urllib3
```

### 3. Configure Parameters (pre-configured, ready to use)
Open `main.py`, core parameters don't need modification, adjust if customization is needed:
```python
# Synology Chat Bot Token
SYNOLOGY_BOT_TOKEN = "PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw"
# ZeroClaw Inbound Interface (default no need to change)
ZEROCLAW_INBOUND = "http://127.0.0.1:42618/webhook/synology"
# Synology Inbound Webhook URL
SYNOLOGY_INCOMING_URL = "https://www.yourdomain.com:5001/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw%22"
# Service Listening Port
LISTEN_PORT = 42619
# Synology User ID (modify according to user ID in Synology Chat)
USER_ID = 6
# Log Language: LogLanguage.ENGLISH or LogLanguage.CHINESE
LOG_LANGUAGE = LogLanguage.ENGLISH
```

**Log Language Switch**:
- `LogLanguage.ENGLISH` - Console logs in English (default)
- `LogLanguage.CHINESE` - Console logs in Chinese

---

## ⚙️ Synology Chat Complete Configuration
### 1. Configure "Bot" (Synology → Relay Service)
1. Open Synology Chat → Click **Profile** in the top right corner → **Integration** → **Bot**
2. Click **Create Bot** and fill in the bot name
3. Configure parameters:
   - Incoming URL: `http://your-server-ip:42619/webhook/synology`
4. Click **OK**, the system will generate and display **Incoming URL** and **Token**
5. Copy the generated **Token** to the `SYNOLOGY_BOT_TOKEN` parameter in `main.py`

---

## 🤖 ZeroClaw Configuration
Configure the Webhook channel in ZeroClaw to connect the relay service with ZeroClaw:

1. Ensure ZeroClaw service is running:
```bash
zeroclaw daemon
```

2. Enter ZeroClaw configuration interface:
```bash
zeroclaw onboard
```

3. Select **Channels** in the configuration menu, then select **webhook**

4. Configure Webhook parameters:
   - `enable`: `y`
   - `port`: `42618`
   - `listen-path`: `/webhook/synology`
   - `send-url`: `http://127.0.0.1:42619/reply`
   - `send-method`: `POST`
   - `auth-header`: (leave empty)
   - `secret`: (leave empty)

5. Save configuration and restart ZeroClaw service

---

## 🚀 Service Management
### 1. Run in Foreground (for testing, view real-time logs)
```bash
python main.py
```

### 2. Run in Background (recommended for production)
```bash
nohup python main.py > /dev/null 2>&1 &
```

### 3. Stop Service
```bash
pkill -f main.py
```

### 4. Check Service Status
```bash
ps aux | grep main.py
```

---

## 📝 Common Commands
```bash
# 1. Install project dependencies
pip install flask requests urllib3

# 2. Start in foreground (view logs)
python main.py

# 3. Start in background (persists after terminal closes)
nohup python main.py > /dev/null 2>&1 &

# 4. Stop service
pkill -f main.py

# 5. Check service process
ps aux | grep main.py
```

---

## ❌ Common Issues (All Resolved)
1. **Error code:120**: Payload format error → Official format compatible
2. **Error code:800**: No target user → User ID configured
3. **Error code:104**: Token error → Official token format matched
4. **Long message truncated**: Automatic segmentation enabled
5. **Service inaccessible**: Check server firewall allows port 42619

---

[中文版本 / Chinese Version](README.md)