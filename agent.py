import json
from typing import Dict, Any, List, Optional, Iterator

import requests
from together import Together
from together.types import ChatCompletionResponse, ChatCompletionChunk
from together.types.chat_completions import ChatCompletionMessage


class SmartAgent:
    def __init__(self):
        self.client = Together(api_key="1aff76ce049d22e115f4b8c7eedabcc6bc5e7d082cbbaeb1bbca72f907971234")
        self.max_iterations = 1  # Max LLM interactions after function call
        self.max_llm_queries = 5
        self.functions = {
            "get_weather": self.get_weather,
            "get_news": self.get_news
        }

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

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> str:
        """Execute the specified function"""
        if function_name not in self.functions:
            return f"Error: Unknown function {function_name}"
        try:
            return self.functions[function_name](**parameters)
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"

    def consult_llm(self, messages: List[Dict[str, str]],tools: Optional[List[Dict[str, Any]]] = None) -> ChatCompletionMessage | None | \
                                                                     dict[
                                                                         str, str]:
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
        messages = [
            {"role": "system", "content": "Use tools when needed. Provide concise answers. you should use tools when necessary. you can use two or more tools."},
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

        # Process function calls
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute function
            function_response = self.functions[function_name](**function_args)

            # Add to conversation
            messages.append({
                "role": "tool",
                "name": function_name,
                "content": function_response,
                "tool_call_id": tool_call.id
            })
        return message


# Example usage
if __name__ == "__main__":
    agent = SmartAgent()

    # # Test case 1: Weather query
    print("\n=== Weather Test ===")
    response = agent.get_refined_response("What's the weather like in Isfahan today?")
    print(agent.call_function(response))

    # Test case 2: News query
    print("\n=== News Test ===")
    response=agent.get_refined_response("What's the news in Tehran today?")
    print(agent.call_function(response))

    # # Test case 3: Combined query
    print("\n=== Combined Test ===")
    response = agent.get_refined_response("Tell me about both weather and news in Isfahan")
    print(agent.call_function(response))

