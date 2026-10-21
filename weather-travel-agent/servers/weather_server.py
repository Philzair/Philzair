# servers/weather_server.py
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather-server")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


async def _geocode(city: str):
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            GEO_URL,
            params={"name": city, "count": 1, "language": "zh", "format": "json"},
        )
        data = resp.json()
        if not data.get("results"):
            raise ValueError(f"无法解析城市：{city}")
        r = data["results"][0]
        return r["latitude"], r["longitude"], r.get("name", city)


@mcp.tool()
async def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气。city 为城市中文名或英文名。"""
    lat, lon, name = await _geocode(city)
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
        )
        cur = resp.json()["current"]
        return (
            f"{name}当前天气：温度 {cur['temperature_2m']}°C，"
            f"湿度 {cur['relative_humidity_2m']}%，"
            f"风速 {cur['wind_speed_10m']} km/h，天气代码 {cur['weather_code']}"
        )


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """获取指定城市从今天开始的未来 N 天天气预报。days 范围 1–7。"""
    lat, lon, name = await _geocode(city)
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                         "precipitation_probability_max,wind_speed_10m_max,uv_index_max",
                "forecast_days": min(max(days, 1), 7),
                "timezone": "auto",
            },
        )
        daily = resp.json()["daily"]
        lines = [f"{name}从今天开始未来 {days} 天预报："]
        for i in range(len(daily["time"])):
            lines.append(
                f"{daily['time'][i]}：{daily['temperature_2m_min'][i]}~{daily['temperature_2m_max'][i]}°C，"
                f"降水概率 {daily['precipitation_probability_max'][i]}%，"
                f"最大风速 {daily['wind_speed_10m_max'][i]} km/h，"
                f"紫外线指数 {daily['uv_index_max'][i]}"
            )
        return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
