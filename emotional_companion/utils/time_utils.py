from datetime import datetime

def get_formatted_time():
    """获取格式化的当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_time_of_day():
    """获取当天的时间段描述"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "早上"
    elif 12 <= hour < 14:
        return "中午"
    elif 14 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "晚上"
    else:
        return "深夜"

def get_greeting():
    """根据时间获取合适的问候语"""
    time_of_day = get_time_of_day()
    greetings = {
        "早上": "早上好",
        "中午": "中午好",
        "下午": "下午好",
        "晚上": "晚上好",
        "深夜": "夜深了"
    }
    return greetings.get(time_of_day, "你好")