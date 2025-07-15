import json
from typing import Dict, Any, List, Optional, Iterator
import datetime
import mark_downs
import requests
import tools_API
from together import Together
from together.types import ChatCompletionResponse, ChatCompletionChunk
from together.types.chat_completions import ChatCompletionMessage


class SmartAgent:
    def __init__(self):
        self.client = Together(api_key="1aff76ce049d22e115f4b8c7eedabcc6bc5e7d082cbbaeb1bbca72f907971234")
        self.max_iterations = 2
        self.max_llm_queries = 5
        self.functions = {
            "get_weather": tools_API.get_weather,
            "get_news": tools_API.get_news,
            "control_device": tools_API.control_device
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
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
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

        weather_data, news_data, control_device = None, None, None
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            result = self.functions[function_name](**function_args)

            if function_name == "get_weather":
                weather_data = result
            elif function_name == "get_news":
                news_data = result
            elif function_name == "control_device":
                control_device = result

        markdown_parts = []
        if weather_data:
            markdown_parts.append(mark_downs.format_weather_En(weather_data))
        if news_data:
            markdown_parts.append(mark_downs.format_news_En(news_data))
        if control_device:
            markdown_parts.append(control_device)

        return "\n\n---\n\n".join(markdown_parts)


# Example usage
if __name__ == "__main__":
    agent = SmartAgent()

    # # Test case 1: Weather query
    print("\n=== Weather Test ===")
    response = agent.get_refined_response("turn on thr lights")
    print(agent.call_function(response))

    # Test case 2: News query
    print("\n=== News Test ===")
    response = agent.get_refined_response("What's the whether in Isfahan?")
    print(agent.call_function(response))

    # # Test case 3: Combined query
    print("\n=== Combined Test ===")
    response = agent.get_refined_response("Tell me about both weather and news in Isfahan")
    print(agent.call_function(response))
