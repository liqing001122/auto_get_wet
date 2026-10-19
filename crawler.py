import os
import requests
import traceback
from datetime import datetime, timezone, timedelta

# ============ 配置区 ============
SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY")
BJT = timezone(timedelta(hours=8))

def fetch_content():
    """
    使用 JSON 接口获取天气，避免纯文本解析的不稳定性
    """
    now = datetime.now(BJT).strftime("%Y-%m-%d %H:%M:%S")
    
    # --- 1. 获取天气 (使用 JSON 格式) ---
    try:
        # format=j1 返回标准 JSON，lang=zh 返回中文
        weather_resp = requests.get("https://wttr.in/Guangzhou?format=j1&lang=zh", timeout=10)
        weather_resp.raise_for_status()  # 如果状态码非200，抛出异常
        w_data = weather_resp.json()
        
        # 提取当前实况数据
        current = w_data['current_condition'][0]
        
        wea = current['lang_zh'][0]['value']  # 天气状况中文
        tem = current['temp_C']               # 温度
        humidity = current['humidity']        # 湿度
        win_dir = current['winddir16Point']   # 风向 (如: 东南)
        win_speed = current['windspeedKmph']  # 风速 (km/h)
        
        weather_text = f"🌤️ 广州今日天气：{wea}，温度{tem}℃，湿度{humidity}%，{win_dir}风 {win_speed}km/h"
        
    except Exception as e:
        print(f"天气获取失败: {str(e)}")
        weather_text = "🌤️ 天气数据获取失败，请稍后重试"

    # --- 2. 获取每日一句 ---
    try:
        say_resp = requests.get("https://v1.hitokoto.cn/?c=i&c=k", timeout=10)
        say_resp.raise_for_status()
        say = say_resp.json()
        say_text = f"📖 每日一句：{say['hitokoto']} —— {say.get('from', '佚名')}"
    except Exception as e:
        print(f"每日一言获取失败: {str(e)}")
        say_text = "📖 今日名言加载失败"

    # --- 3. 拼接内容 ---
    title = f"每日爬虫推送 | {now[:10]}"
    content = f"""
### ⏰ 推送时间
{now}

---

{weather_text}

---

{say_text}

---
⚠️ 本消息由GitHub Actions自动发送
    """
    return title, content

def push_to_wechat(title, content):
    """调用Server酱接口推送到微信"""
    if not SERVERCHAN_KEY:
        print("未配置SERVERCHAN_KEY，跳过推送")
        return
    
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    data = {
        "title": title,
        "desp": content
    }
    
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        print("推送结果：", resp.json())
    except Exception as e:
        print(f"微信推送失败: {str(e)}")

if __name__ == "__main__":
    try:
        print("开始执行爬虫...")
        title, content = fetch_content()
        print("爬取完成，开始推送...")
        push_to_wechat(title, content)
        print("全部执行完成！")
    except Exception as e:
        error_msg = f"爬虫执行出错：{str(e)}\n\n错误详情：\n{traceback.format_exc()}"
        print(error_msg)
        # 尝试推送错误信息，如果连推送都失败了，至少控制台有日志
        try:
            push_to_wechat("❌ 爬虫运行失败", error_msg)
        except:
            pass
        exit(1)
