from typing import Dict, Any, List, Optional, Iterator
import requests
import datetime


def get_weather(location: str):
    print("weather")
    open_weather_api_key = "56790bf75f7f78cc009b8f461daa6358"
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={open_weather_api_key}&units=metric"
    try:
        data = requests.get(url, timeout=30).json()
        forecasts = []
        today = datetime.datetime.today().date()
        for entry in data.get("list", []):
            dt = datetime.datetime.fromtimestamp(entry["dt"]).date()
            if dt < today:
                continue
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
            if len(forecasts) >= 3:
                break
        if not forecasts:
            return {
                "location": location,
                "forecasts": [],
                "status": "no data available"
            }
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
    print("news")
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


def control_device(devices: List[Dict[str, str]], house_elements: Dict[str, List]) -> str:
    code = ''
    not_found_devices = []

    for entry in devices:
        target_device = entry.get("device")
        action = entry.get("action")
        action_value = 0b1 if action == "on" else 0b0

        if not target_device or not action:
            continue

        device_found = False
        for room, device_list in house_elements.items():
            for device_name, device_code in device_list:
                if device_name.lower() == target_device.lower():
                    device_found = True
                    code += str(device_code + action_value)

        if not device_found:
            not_found_devices.append(target_device)

    if not code:
        return "No valid devices were found to control."

    response_msg = send_command_to_esp32(code)

    if not_found_devices:
        not_found_str = ", ".join(not_found_devices)
        response_msg += f"\nNote: The following devices were not found in the house: {not_found_str}"

    return response_msg


def send_command_to_esp32(device_code: str) -> str:
    try:
        esp32_ip = "http://192.168.1.50"
        url = f"{esp32_ip}/control"
        params = {"cmd": device_code}

        response = requests.get(url, params=params, timeout=20)

        if response.status_code == 200:
            try:
                code = int(response.text.strip())
                if code == 2:
                    return "Command sent successfully and executed."
                elif code == 3:
                    return "Command sent, but no response from Arduino."
                elif code == 4:
                    return "Command sent, but some instructions failed."
                else:
                    return f"Unknown response code from device: {code}"
            except ValueError:
                return f"Invalid response format: {response.text}"
        elif response.status_code == 400:
            return "Bad request. The URL or parameters may be incorrect."
        else:
            return f"Request failed with status code: {response.status_code}"

    except requests.exceptions.Timeout:
        return "Request timed out. ESP32 may be unreachable."
    except requests.exceptions.ConnectionError:
        return "Failed to connect to ESP32. Please check the network."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
