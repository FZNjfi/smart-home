import json
from typing import Dict, Any, List, Optional, Iterator
import datetime
import mark_downs
import requests
from together import Together
from together.types import ChatCompletionResponse, ChatCompletionChunk
from together.types.chat_completions import ChatCompletionMessage


class SmartAgent:
    def __init__(self):
        self.client = Together(api_key="1aff76ce049d22e115f4b8c7eedabcc6bc5e7d082cbbaeb1bbca72f907971234")
        self.max_iterations = 2
        self.max_llm_queries = 5
        self.functions = {
            "get_weather": self.get_weather,
            "get_news": self.get_news
        }
        self.house_structure = {
            "Living Room": ["TV"],
            "Bathroom": ["lamp"],
            "Kitchen": ["lamp", "air conditioner"],
            "Room 1": ["lamp", "air conditioner"],
            "Room2": ["lamp"]
        }

    def get_house_description(self) -> str:
        lines = ["This house has the following rooms and devices:"]
        for room, devices in self.house_structure.items():
            lines.append(f"- {room}: {', '.join(devices)}")
        return "\n".join(lines)

    def get_weather(self, location: str):
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

    def get_news(self, location: str) -> str:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": location,
            "apiKey": "17fa3ca9e3f84f188474b560074d487d"
        }
        response = requests.get(url, params=params)

        # Check for success
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            summaries = [f"{i + 1}. {a['title']}" for i, a in enumerate(articles[:5])]
            return "\n".join(summaries)
        else:
            print(f"Request failed with status code {response.status_code}")

        return f"the weather in {location} is good"

    def control_device(self, devices: List[Dict[str, str]]) -> str:
        result = []
        for entry in devices:
            device = entry.get("device")
            action = entry.get("action")
            room = entry.get("room", "نامشخص")
            if device and action:
                result.append(f"🔌 دستگاه **{device}** در اتاق **{room}** به حالت **{action.upper()}** تنظیم شد.")
        return "\n".join(result) if result else "هیچ دستگاهی تنظیم نشد."

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> str:
        """Execute the specified function"""
        if function_name not in self.functions:
            return f"Error: Unknown function {function_name}"
        try:
            return self.functions[function_name](**parameters)
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"

    def consult_llm(self, messages: List[Dict[str, str]],
                    tools: Optional[List[Dict[str, Any]]] = None):
        """Consult the LLM with proper error handling"""
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",  # Updated model name
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )
            return response.choices[0].message
        except Exception as e:
            print(f"Error consulting LLM: {str(e)}")
            return {"content": "I encountered an error processing your request."}

    def get_refined_response(self, user_query: str) -> None | ChatCompletionResponse | Iterator[ChatCompletionChunk]:
        """Get optimal response with max 5 LLM consultations"""
        response = None
        house_info = self.get_house_description()
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a smart home assistant. Use tools when needed. "
                    f"You can call multiple tools if required.\n\n"
                    f"{house_info}\n\n"
                    f"Each device can be turned 'on' or 'off'."
                )
            },
            {"role": "user", "content": user_query}
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Call this function ONLY if the user is asking about weather in a specific city or country.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_news",
                    "description": "Call this function ONLY if the user is asking about news in a specific city or country.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_device",
                    "description": "Use this to turn devices on or off, for multiple devices at once.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "devices": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "device": {"type": "string"},
                                        "action": {"type": "string", "enum": ["on", "off"]}
                                    },
                                    "required": ["device", "action"]
                                }
                            }
                        },
                        "required": ["devices"]
                    }
                }
            }

        ]

        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.1
            )

        return response

    def call_function(self, response):
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content

        weather_data, news_data = None, None
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            result = self.functions[function_name](**function_args)

            if function_name == "get_weather":
                weather_data = result
            elif function_name == "get_news":
                news_data = result

        markdown_parts = []
        if weather_data:
            markdown_parts.append(mark_downs.format_weather_markdown(weather_data))
        if news_data:
            markdown_parts.append(mark_downs.format_news_markdown(news_data))

        return "\n\n---\n\n".join(markdown_parts)


# Example usage
if __name__ == "__main__":
    agent = SmartAgent()

    # # Test case 1: Weather query
    print("\n=== Weather Test ===")
    response = agent.get_refined_response("من رسیدم")
    print(agent.call_function(response))

    # Test case 2: News query
    print("\n=== News Test ===")
    response = agent.get_refined_response("What's the news in Tehran today?")
    print(agent.call_function(response))

    # # Test case 3: Combined query
    print("\n=== Combined Test ===")
    response = agent.get_refined_response("Tell me about both weather and news in Isfahan")
    print(agent.call_function(response))
