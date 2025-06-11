from together import Together
import json
import datetime
import requests


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


def get_response():
    client = Together(api_key="1aff76ce049d22e115f4b8c7eedabcc6bc5e7d082cbbaeb1bbca72f907971234")

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[

            {"role": "system", "content": "Only call a function if absolutely necessary."},
            {"role": "user", "content": "is Isfahan today sunny"}

        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Call this function ONLY if the user is asking about weather in a specific city or country.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to get the weather for."
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    )
    return response


def call_function(response):
    message = response.choices[0].message
    print(message)
    if message.tool_calls:
        function_name = message.tool_calls[0].function.name
        arguments = message.tool_calls[0].function.arguments
        parsed_args = json.loads(arguments)
        result = globals()[function_name](**parsed_args)
        print(result)


response = get_response()
call_function(response)
