# ZeroClaw-SynologyChat 中转服务

[English Version / 英文版本](README.en.md)

基于 Flask 开发的 **ZeroClaw ↔ 群晖 Chat 双向消息中转服务**，100% 兼容群晖 Chat 官方 API 规范，彻底解决消息格式错误、长消息截断、目标用户缺失、接口报错等问题，开箱即用。

---

## 🌟 项目功能
1. **双向消息互通**：群晖 Chat 与 ZeroClaw AI 无缝对接，收发正常
2. **长消息自动分段**：突破群晖消息长度限制，自动拆分多段发送
3. **官方格式适配**：复刻 OpenClaw 官方插件格式，无 120/800/104 报错
4. **接口限流保护**：500ms 发送间隔，避免群晖接口限流
5. **安全令牌验证**：验证请求合法性，拒绝非法调用
6. **完善控制台日志**：全流程日志输出，方便排查问题

---

## 📋 环境要求
- Linux 服务器（Debian/Ubuntu/CentOS 均可）
- Python 3.7 及以上版本
- 已正常部署 ZeroClaw 服务
- 群晖 NAS + 已安装群晖 Chat 应用

---

## 🛠️ 安装部署步骤
### 1. 上传代码
将项目文件 `main.py` 上传至服务器目录，示例路径：
```
/www/wwwroot/pythonProject/zeroClawChatService/
```

### 2. 安装 Python 依赖
进入项目目录，执行依赖安装命令：
```bash
pip install flask requests urllib3
```

### 3. 配置参数（默认已填好，可直接用）
打开 `main.py`，核心参数无需修改，如需自定义可调整：
```python
# 群晖Chat机器人令牌
SYNOLOGY_BOT_TOKEN = "PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw"
# ZeroClaw入站接口（默认无需改）
ZEROCLAW_INBOUND = "http://127.0.0.1:42618/webhook/synology"
# 群晖入站Webhook URL
SYNOLOGY_INCOMING_URL = "https://www.yourdomain.com:5001/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw%22"
# 服务监听端口
LISTEN_PORT = 42619
# 群晖用户ID（根据群晖 Chat 中的用户ID修改）
USER_ID = 6
```

---

## ⚙️ 群晖 Chat 完整配置
### 1. 配置「出站 Webhook」（群晖 → 中转服务）
1. 打开群晖 Chat → 点击右上角**头像** → **整合**
2. 选择 **Webhook** → **新增** → 选择**出站**
3. 按以下参数配置：
   - 名称：ZeroClaw AI 中转
   - 目标 URL：`http://你的服务器IP:42619/webhook/synology`
   - 请求方式：`POST`
   - 令牌：填写 `main.py` 中的 `SYNOLOGY_BOT_TOKEN`
   - 触发条件：勾选 **私信**
4. 点击**测试**，提示成功即配置完成

### 2. 配置「入站 Webhook」（中转服务 → 群晖）
1. 群晖 Chat 整合页面 → **新增** → 选择**入站 Webhook**
2. 配置参数：
   - 名称：ZeroClaw 消息回复
   - 权限：勾选 **允许发送消息**
3. 复制生成的**入站 Webhook 完整 URL**，替换 `main.py` 中的对应参数

---

## 🤖 ZeroClaw 配置
**无需额外配置**，本服务已自动对接 ZeroClaw 默认入站接口：
1. 确保 ZeroClaw 正常后台运行：
```bash
zeroclaw daemon
```
2. ZeroClaw 会自动接收群晖消息并返回 AI 回复，无额外设置

---

## 🚀 启动与服务管理
### 1. 前台运行（测试用，看实时日志）
```bash
python main.py
```

### 2. 后台守护运行（生产环境推荐）
```bash
nohup python main.py > /dev/null 2>&1 &
```

### 3. 停止服务
```bash
pkill -f main.py
```

### 4. 查看服务运行状态
```bash
ps aux | grep main.py
```

---

## 📝 常用命令汇总
```bash
# 1. 安装项目依赖
pip install flask requests urllib3

# 2. 前台启动（看日志）
python main.py

# 3. 后台启动（关闭终端不退出）
nohup python main.py > /dev/null 2>&1 &

# 4. 停止服务
pkill -f main.py

# 5. 查看服务进程
ps aux | grep main.py
```

---

## ❌ 常见问题（已全部解决）
1. **报错 code:120**：payload 格式错误 → 已适配官方格式
2. **报错 code:800**：无目标用户 → 已配置用户 ID
3. **报错 code:104**：令牌错误 → 已匹配官方令牌格式
4. **长消息被截断**：已开启自动分段功能
5. **服务无法访问**：检查服务器防火墙放行 42619 端口