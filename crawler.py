import os
import requests
import traceback
from datetime import datetime, timezone, timedelta

# ============ 配置区（不用改，密钥从GitHub Secrets自动读取） ============
SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY")  # 微信推送密钥
# 北京时间时区
BJT = timezone(timedelta(hours=8))

def fetch_content():
    """
    这里写你的爬虫逻辑，返回(消息标题, 消息正文)即可
    下面是示例：爬取北京天气+每日一句，你可以替换成自己的爬取代码
    """
    # 示例1：获取当前北京时间
    now = datetime.now(BJT).strftime("%Y-%m-%d %H:%M:%S")
    
    # 示例2：调用免费天气接口（你可以换成自己想爬的网站）
    weather_resp = requests.get("https://www.tianqiapi.com/free/day?appid=23035354&appsecret=8YvlPNrz&city=北京", timeout=10)
    weather = weather_resp.json()
    weather_text = f"🌤️ 北京今日天气：{weather['wea']}，温度{weather['tem']}℃，{weather['win']}{weather['win_speed']}"
    
    # 示例3：获取每日一句
    say_resp = requests.get("https://v1.hitokoto.cn/?c=i&c=k", timeout=10)
    say = say_resp.json()
    say_text = f"📖 每日一句：{say['hitokoto']} —— {say.get('from', '佚名')}"

    # 拼接消息内容
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
    resp = requests.post(url, data=data, timeout=10)
    print("推送结果：", resp.json())

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
        push_to_wechat("❌ 爬虫运行失败", error_msg)
        exit(1)
