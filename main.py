from flask import Flask, request
import requests
import json
import time
import urllib.parse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===================== 配置 =====================
SYNOLOGY_BOT_TOKEN = "PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw"
ZEROCLAW_INBOUND = "http://127.0.0.1:42618/webhook/synology"
SYNOLOGY_INCOMING_URL = "https://www.yourSynologyDomain.com:5001/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw%22"
LISTEN_PORT = 42619
MAX_SEGMENT_LENGTH = 500
MIN_SEND_INTERVAL_MS = 500
USER_ID = 6
# ===================================================

app = Flask(__name__)

# 简易控制台日志（无文件，纯输出）
def log_info(msg):
    print(f"[INFO] {time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}")
def log_error(msg):
    print(f"[ERROR] {time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

# 官方分段函数
def split_message(text, max_length):
    segments = []
    current = ""
    lines = text.split('\n')
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            if current:
                segments.append(current.strip())
                current = ""
        current += line + '\n'
    if current.strip():
        segments.append(current.strip())
    return segments

# -------------- 群晖 → ZeroClaw --------------
@app.route('/webhook/synology', methods=['POST'])
def synology_to_zeroclaw():
    data = request.form
    if data.get('token') != SYNOLOGY_BOT_TOKEN:
        log_error("令牌验证失败，拒绝请求")
        return "NO", 403
    
    msg = data.get('text', '').strip()
    username = data.get('username', 'user')
    log_info(f"收到群晖消息 | 用户: {username} | 内容: {msg}")
    
    try:
        requests.post(
            ZEROCLAW_INBOUND,
            json={"sender": username, "content": msg},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        log_info("消息已转发至ZeroClaw")
    except Exception as e:
        log_error(f"转发ZeroClaw失败: {str(e)}")
    return "OK", 200

# -------------- ZeroClaw → 群晖（100%复刻官方+完善日志）--------------
@app.route('/reply', methods=['POST'])
def zeroclaw_to_synology():
    raw = request.get_data(as_text=True)
    log_info(f"收到ZeroClaw回复原始数据: {raw[:100]}...")

    # 解析AI回复
    try:
        ai_msg = json.loads(raw).get("content", "")
        log_info(f"解析AI回复成功 | 内容长度: {len(ai_msg)} 字符")
    except:
        ai_msg = raw.strip()
        log_info(f"非JSON格式，直接使用原始文本 | 长度: {len(ai_msg)} 字符")

    if not ai_msg:
        log_info("回复内容为空，终止发送")
        return "OK", 200

    # 分段处理
    segments = split_message(ai_msg, MAX_SEGMENT_LENGTH)
    log_info(f"消息自动分段完成 | 总段数: {len(segments)}")

    last_send_time = 0
    for i, segment in enumerate(segments):
        # 官方限流
        now = int(time.time() * 1000)
        elapsed = now - last_send_time
        if elapsed < MIN_SEND_INTERVAL_MS:
            wait_time = (MIN_SEND_INTERVAL_MS - elapsed) / 1000
            log_info(f"限流等待 {wait_time} 秒")
            time.sleep(wait_time)

        log_info(f"开始发送第 {i+1}/{len(segments)} 段 | 内容: {segment[:50]}...")
        
        # 官方发送格式
        payload_obj = {
            "text": segment,
            "user_ids": [USER_ID]
        }
        payload = json.dumps(payload_obj, ensure_ascii=False)
        body = f"payload={urllib.parse.quote(payload)}"

        try:
            res = requests.post(
                SYNOLOGY_INCOMING_URL,
                data=body,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Content-Length": str(len(body.encode('utf-8')))
                },
                verify=False,
                timeout=10
            )
            last_send_time = int(time.time() * 1000)
            log_info(f"群晖接口返回: {res.text}")
            
            if '"success":true' in res.text:
                log_info(f"✅ 第 {i+1} 段发送成功！")
            else:
                log_error(f"❌ 第 {i+1} 段发送失败")
        except Exception as e:
            log_error(f"发送请求异常: {str(e)}")

    log_info("="*50)
    return "OK", 200

if __name__ == '__main__':
    log_info("🚀 【OpenClaw官方复刻版】服务启动成功")
    log_info(f"监听端口: {LISTEN_PORT} | 消息分段: {MAX_SEGMENT_LENGTH}字符/段")
    log_info(f"群晖Webhook地址: http://0.0.0.0:{LISTEN_PORT}/webhook/synology")
    app.run(host='0.0.0.0', port=LISTEN_PORT, debug=False)