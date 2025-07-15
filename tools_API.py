from typing import Dict, Any, List, Optional, Iterator
import requests
import datetime


def get_weather(location: str):
    open_weather_api_key = "56790bf75f7f78cc009b8f461daa6358"
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={open_weather_api_key}&units=metric"
    try:
        data = requests.get(url, timeout=30).json()
        forecasts = []

        for entry in data.get("list", []):
            dt = datetime.datetime.fromtimestamp(entry["dt"]).date()
            if dt == datetime.datetime.today().date():
                forecasts.append({
                    "timestamp": entry["dt"],
                    "date": dt.isoformat(),
                    "weather": entry["weather"][0]["description"],
                    "temperature": entry["main"]["temp"],
                    "feels_like": entry["main"]["feels_like"],
                    "humidity": entry["main"]["humidity"],
                    "wind_speed": entry["wind"]["speed"],
                    "pressure": entry["main"]["pressure"]
                })
            else:
                break

        return {
            "location": location,
            "forecasts": forecasts,
            "status": "success" if forecasts else "no data available"
        }
    except Exception as e:
        return {
            "location": location,
            "forecasts": [],
            "status": "error",
            "error_message": str(e)
        }


def get_news(location: str) -> str:
    # url = "https://newsapi.org/v2/top-headlines"
    # params = {
    #     "country": location,
    #     "apiKey": "17fa3ca9e3f84f188474b560074d487d"
    # }
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": location,
        "token": "2480fcc7209dc960db61738b9ec267c6",
        "lang": "en",
        "max": 5
    }
    response = requests.get(url, params=params)

    # Check for success
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        summaries = [f"{i + 1}. {a['title']}" for i, a in enumerate(articles[:5])]
        return "\n".join(summaries)
    else:
        print(f"Request failed with status code {response.status_code}")
        return str(response.status_code)




def control_device(devices: List[Dict[str, str]]) -> str:
    result = []
    for entry in devices:
        device = entry.get("device")
        action = entry.get("action")
        if device and action:
            result.append(f"")
    return "\n".join(result) if result else "هیچ دستگاهی تنظیم نشد."