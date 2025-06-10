from together import Together
import json


def get_weather(location:str):
    return f"the weather in {location} is good"

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



