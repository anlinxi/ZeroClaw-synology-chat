from flask import Flask, request
import requests
import json
import time
import urllib.parse
import urllib3
from enum import Enum

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LogLanguage(Enum):
    CHINESE = "zh"
    ENGLISH = "en"

# ===================== 配置 =====================
SYNOLOGY_BOT_TOKEN = "PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw"
ZEROCLAW_INBOUND = "http://127.0.0.1:42618/webhook/synology"
SYNOLOGY_INCOMING_URL = "https://www.yourSynologyDomain.com:5001/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22PTi6SChbYLOLOoz1ieZMeO7dR1ls2t5QThx3CT74Bz9vMEa3wd4k6iB3PXR1wqXw%22"
LISTEN_PORT = 42619
MAX_SEGMENT_LENGTH = 500
MIN_SEND_INTERVAL_MS = 500
USER_ID = 6
# 日志语言 LANGUAGE
LOG_LANGUAGE = LogLanguage.ENGLISH
# ===================================================

LOG_MESSAGES = {
    LogLanguage.CHINESE: {
        "token_verification_failed": "令牌验证失败，拒绝请求",
        "received_synology_message": "收到群晖消息 | 用户: {username} | 内容: {msg}",
        "forwarded_to_zeroclaw": "消息已转发至ZeroClaw",
        "forward_failed": "转发ZeroClaw失败: {error}",
        "received_zeroclaw_reply": "收到ZeroClaw回复原始数据: {data}",
        "parsed_ai_reply_success": "解析AI回复成功 | 内容长度: {length} 字符",
        "non_json_format": "非JSON格式，直接使用原始文本 | 长度: {length} 字符",
        "empty_reply": "回复内容为空，终止发送",
        "message_segmented": "消息自动分段完成 | 总段数: {count}",
        "rate_limit_wait": "限流等待 {wait_time} 秒",
        "sending_segment": "开始发送第 {current}/{total} 段 | 内容: {content}",
        "synology_response": "群晖接口返回: {response}",
        "segment_sent_success": "✅ 第 {segment} 段发送成功！",
        "segment_sent_failed": "❌ 第 {segment} 段发送失败",
        "send_request_exception": "发送请求异常: {error}",
        "service_started": "🚀 【OpenClaw官方复刻版】服务启动成功",
        "listen_port_info": "监听端口: {port} | 消息分段: {segment_length}字符/段",
        "synology_webhook_url": "群晖Webhook地址: {url}"
    },
    LogLanguage.ENGLISH: {
        "token_verification_failed": "Token verification failed, request rejected",
        "received_synology_message": "Received Synology message | User: {username} | Content: {msg}",
        "forwarded_to_zeroclaw": "Message forwarded to ZeroClaw",
        "forward_failed": "Failed to forward to ZeroClaw: {error}",
        "received_zeroclaw_reply": "Received ZeroClaw reply raw data: {data}",
        "parsed_ai_reply_success": "AI reply parsed successfully | Content length: {length} characters",
        "non_json_format": "Non-JSON format, using raw text directly | Length: {length} characters",
        "empty_reply": "Reply content is empty, terminating send",
        "message_segmented": "Message segmented automatically | Total segments: {count}",
        "rate_limit_wait": "Rate limit wait {wait_time} seconds",
        "sending_segment": "Sending segment {current}/{total} | Content: {content}",
        "synology_response": "Synology API response: {response}",
        "segment_sent_success": "✅ Segment {segment} sent successfully!",
        "segment_sent_failed": "❌ Segment {segment} failed to send",
        "send_request_exception": "Send request exception: {error}",
        "service_started": "🚀 [OpenClaw Official Clone] Service started successfully",
        "listen_port_info": "Listening port: {port} | Message segment: {segment_length} chars/segment",
        "synology_webhook_url": "Synology Webhook URL: {url}"
    }
}

app = Flask(__name__)

def get_log_message(key, **kwargs):
    messages = LOG_MESSAGES.get(LOG_LANGUAGE, LOG_MESSAGES[LogLanguage.CHINESE])
    message = messages.get(key, key)
    return message.format(**kwargs)

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
        log_error(get_log_message("token_verification_failed"))
        return "NO", 403
    
    msg = data.get('text', '').strip()
    username = data.get('username', 'user')
    log_info(get_log_message("received_synology_message", username=username, msg=msg))
    
    try:
        requests.post(
            ZEROCLAW_INBOUND,
            json={"sender": username, "content": msg},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        log_info(get_log_message("forwarded_to_zeroclaw"))
    except Exception as e:
        log_error(get_log_message("forward_failed", error=str(e)))
    return "OK", 200

# -------------- ZeroClaw → 群晖（100%复刻官方+完善日志）--------------
@app.route('/reply', methods=['POST'])
def zeroclaw_to_synology():
    raw = request.get_data(as_text=True)
    log_info(get_log_message("received_zeroclaw_reply", data=raw[:100] + "..."))

    # 解析AI回复
    try:
        ai_msg = json.loads(raw).get("content", "")
        log_info(get_log_message("parsed_ai_reply_success", length=len(ai_msg)))
    except:
        ai_msg = raw.strip()
        log_info(get_log_message("non_json_format", length=len(ai_msg)))

    if not ai_msg:
        log_info(get_log_message("empty_reply"))
        return "OK", 200

    # 分段处理
    segments = split_message(ai_msg, MAX_SEGMENT_LENGTH)
    log_info(get_log_message("message_segmented", count=len(segments)))

    last_send_time = 0
    for i, segment in enumerate(segments):
        # 官方限流
        now = int(time.time() * 1000)
        elapsed = now - last_send_time
        if elapsed < MIN_SEND_INTERVAL_MS:
            wait_time = (MIN_SEND_INTERVAL_MS - elapsed) / 1000
            log_info(get_log_message("rate_limit_wait", wait_time=wait_time))
            time.sleep(wait_time)

        log_info(get_log_message("sending_segment", current=i+1, total=len(segments), content=segment[:50] + "..."))
        
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
            log_info(get_log_message("synology_response", response=res.text))
            
            if '"success":true' in res.text:
                log_info(get_log_message("segment_sent_success", segment=i+1))
            else:
                log_error(get_log_message("segment_sent_failed", segment=i+1))
        except Exception as e:
            log_error(get_log_message("send_request_exception", error=str(e)))

    log_info("="*50)
    return "OK", 200

if __name__ == '__main__':
    log_info(get_log_message("service_started"))
    log_info(get_log_message("listen_port_info", port=LISTEN_PORT, segment_length=MAX_SEGMENT_LENGTH))
    log_info(get_log_message("synology_webhook_url", url=f"http://0.0.0.0:{LISTEN_PORT}/webhook/synology"))
    app.run(host='0.0.0.0', port=LISTEN_PORT, debug=False)