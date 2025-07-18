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
        self.client = Together(api_key="e94227043f583bbf3a480d8dc6017a0a906762fe3daa5a7e3fff1d81b8ac600c")
        self.max_iterations = 4
        self.max_llm_queries = 5
        self.functions = {
            "get_weather": tools_API.get_weather,
            "get_news": tools_API.get_news,
            "control_device": tools_API.control_device
        }
        self.house_structure = {
            "Living Room": [("TV", 0b0100001)],
            "Bathroom": [("lamp", 0b0101000)],
            "Kitchen": [("lamp", 0b0100111), ("air conditioner", 0b0100100)],
            "Room 1": [("lamp", 0b0100101), ("air conditioner", 0b0100010)],  # servo
            "Room2": [("lamp", 0b0100110)]
        }

    def get_house_description(self) -> str:
        lines = ["This house has the following rooms and devices:"]
        for room, devices in self.house_structure.items():
            device_names = [name for (name, _) in devices]
            lines.append(f"- {room}: {', '.join(device_names)}")
        return "\n".join(lines)

    def set_prompt(self, prompt):
        house_info = self.get_house_description()
        is_farsi = self.is_persian(prompt)

        if is_farsi:
            system_prompt = (
                f"تو یک دستیار خانه هوشمند هستی. وقتی لازم بود از ابزار استفاده کن. "
                f" میتونی چند ابزار رو همزمان استفاده کنی.\n\n"
                f"{house_info}\n\n"
                f"\nهر دستگاه می‌تونه 'روشن' یا 'خاموش' بشه."
                f"متن جواب کاملا فارسی باشد.\n"
                f"\nاگر دیگر نیازی به ابزار نبود جواب نهایی را بگردان و ابزاری صدا نزن."
                f"باید از داده های آن ابزار که صدا زدی در متن استفاده کنی."
            )
        else:
            system_prompt = (
                f"You are a smart home assistant. Use tools when needed. "
                f"You can call multiple tools if required.\n\n"
                f"{house_info}\n\n"
                f"Each device can be turned 'on' or 'off'."
                f"You can use tools as many times as needed, but once you have all the information you need, stop calling tools and provide the final answer."
                f"You should use data of a tool which you call."
            )
        return system_prompt

    def agent_loop(self, prompt):
        called_tools = set()
        messages = [
            {"role": "system", "content": self.set_prompt(prompt)},
            {"role": "user", "content": prompt}
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Call this function ONLY if the user is asking about weather in a specific city or country. If city or country is in Persian, translate it to English.",
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
                    "description": "Call this function ONLY if the user is asking about news in a specific city or country. If city or country is in Persian, translate it to English.",
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
                                        "room": {"type": "string"},
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
        message=''
        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=messages,
                tool_choice="auto",
                tools=tools,
                temperature=0.1
            )
            message = response.choices[0].message

            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    key = (tool_call.function.name, json.dumps(args, sort_keys=True))
                    if key in called_tools:
                        continue

                    called_tools.add(key)
                    result = self.functions[tool_call.function.name](**args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": self.call_mark_down(result, tool_call.function.name, self.is_persian(prompt))
                    })

                messages.append({"role": "assistant", "content": None, "tool_calls": message.tool_calls})
                continue

            messages.append({"role": "assistant", "content": message.content})
            return message.content
        return message.content

    def call_mark_down(self, result, function_name, is_persian):
        markdown=''
        if is_persian:
            if function_name == "get_weather":
                markdown = mark_downs.format_weather_FA(result)
            elif function_name == "get_news":
                markdown = mark_downs.format_news_FA(result)
            elif function_name == "control_device":
                markdown = mark_downs.format_device_control_FA(result)
        else:
            if function_name == "get_weather":
                markdown=mark_downs.format_weather_En(result)
            elif function_name == "get_news":
                markdown=mark_downs.format_news_En(result)
            elif function_name == "control_device":
                markdown = result

        return markdown

    def is_persian(self, text: str) -> bool:
        return any('\u0600' <= char <= '\u06FF' for char in text)


# Example usage
if __name__ == "__main__":
    agent = SmartAgent()

    # # Test case 1: Weather query
    print("\n=== Weather Test ===")
    response = agent.agent_loop("راجب اخبار و آب و هوای اصفهان بگو و کولر را روشن کن")
    print(response)

    # Test case 2: News query
    # print("\n=== News Test ===")
    # response = agent.agent_loop("What's the whether in Isfahan?")
    # print(response)

    # # Test case 3: Combined query
    # print("\n=== Combined Test ===")
    # response = agent.agent_loop("Oh the weather is hot!!")
    # print(response)
