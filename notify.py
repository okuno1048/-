import os
import datetime
import requests


def get_nth_weekday(year, month, weekday, n):
    """月の第n曜日の日付を返す (weekday: 0=月, 4=金)"""
    count = 0
    day = datetime.date(year, month, 1)
    while day.month == month:
        if day.weekday() == weekday:
            count += 1
            if count == n:
                return day
        day += datetime.timedelta(days=1)
    return None


def get_garbage_types(target_date):
    year = target_date.year
    month = target_date.month
    weekday = target_date.weekday()  # 0=月, 4=金

    types = []

    # プラゴミ: 第2・第4金曜日
    if weekday == 4:
        for n in [2, 4]:
            if get_nth_weekday(year, month, 4, n) == target_date:
                types.append("プラゴミ")
                break

    # 資源ゴミ（缶・瓶・ペットボトル）: 第1・第3月曜日
    if weekday == 0:
        for n in [1, 3]:
            if get_nth_weekday(year, month, 0, n) == target_date:
                types.append("資源ゴミ（缶・瓶・ペットボトル）")
                break

    # 粗大ゴミ: 第1金曜日
    if weekday == 4:
        if get_nth_weekday(year, month, 4, 1) == target_date:
            types.append("粗大ゴミ")

    return types


def send_line_message(token, group_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": group_id,
        "messages": [{"type": "text", "text": message}],
    }
    res = requests.post(url, headers=headers, json=payload)
    res.raise_for_status()


def main():
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    group_id = os.environ["LINE_GROUP_ID"]

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    types = get_garbage_types(tomorrow)

    if not types:
        print("明日はゴミの日ではありません。通知なし。")
        return

    weekday_names = ["月", "火", "水", "木", "金", "土", "日"]
    date_str = f"{tomorrow.month}月{tomorrow.day}日({weekday_names[tomorrow.weekday()]})"
    types_str = "・".join(types)

    message = (
        f"🗑️ 明日 {date_str} は\n"
        f"【{types_str}】の日です！\n"
        f"ゴミを出す準備をしましょう♪"
    )

    send_line_message(token, group_id, message)
    print(f"通知送信完了: {types_str}")


if __name__ == "__main__":
    main()
