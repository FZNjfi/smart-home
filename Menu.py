import asyncio

import agent
from agent import SmartAgent
import convert_speech_test


def menu():
    agent = SmartAgent()
    speech = convert_speech_test.Speech()
    while True:
        print("\n--- Main Menu ---")
        print("1. Voice Question → Text Answer")
        print("2. Text Question → Text Answer")
        print("3. Voice Question → Voice Answer")
        print("4. Text Question → Voice Answer")
        print("0. Exit")

        choice = input("👉 Enter your choice: ")

        if choice == "1":
            speech.audio_record()
            message = speech.convert_speech_to_text()
            response = agent.agent_loop(message)
            print("📄 ", response)

        elif choice == "2":
            question = input("📝 Enter your question: ")
            response = agent.agent_loop(question)
            print("📄 ", response)

        elif choice == "3":
            speech.audio_record()
            message = speech.convert_speech_to_text()
            response = agent.agent_loop(message)
            print("📄 ", response)
            asyncio.run(speech.convert_text_to_speech(response))

        elif choice == "4":
            question = input("📝 Enter your question: ")
            response = agent.agent_loop(question)
            print("📄 ", response)
            asyncio.run(speech.convert_text_to_speech(response))

        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❗ Invalid option. Try again.")


if __name__ == "__main__":
    menu()
