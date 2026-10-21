# servers/travel_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel-server")


@mcp.tool()
def suggest_travel_plan(
    city: str,
    weather_summary: str,
    temp_min: float,
    temp_max: float,
    precipitation_prob: int,
    wind_speed_max: float,
    uv_index: float,
    preference: str = "综合",
) -> str:
    """根据天气数据生成出行建议。
    preference 可选：户外、室内、带娃、摄影、综合。
    """
    tips = []

    if precipitation_prob >= 60:
        tips.append("降水概率较高，建议携带雨具，优先安排室内活动（博物馆、商场、咖啡馆）。")
    elif precipitation_prob >= 30:
        tips.append("可能有零星降水，建议随身带折叠伞，户外活动预留备选方案。")
    else:
        tips.append("降水概率低，适合户外活动。")

    if temp_max >= 32:
        tips.append("气温较高，建议避开 11:00–15:00 的暴晒时段，注意补水防晒。")
    elif temp_min <= 5:
        tips.append("早晚较冷，建议分层穿衣，携带外套。")
    else:
        tips.append("温度较为舒适，正常穿着即可。")

    if wind_speed_max >= 25:
        tips.append("风力较大，不建议骑行或进行高空/水上项目。")
    if uv_index >= 7:
        tips.append("紫外线较强，建议涂抹防晒霜、佩戴帽子和墨镜。")

    if preference == "户外" and precipitation_prob < 40:
        tips.append("结合你的户外偏好，推荐公园、徒步或滨水区域。")
    elif preference == "室内" or precipitation_prob >= 60:
        tips.append("推荐室内备选：博物馆、展览馆、书店或特色餐厅。")
    elif preference == "带娃":
        tips.append("带娃出行建议优先选择亲子友好场所，并预留室内备选，避免长时间暴晒或淋雨。")

    return f"【{city}出行建议】\n" + "\n".join(f"- {t}" for t in tips)


if __name__ == "__main__":
    mcp.run()