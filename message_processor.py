import asyncio
import websockets
import os


async def handle_message(websocket, path=None):  # Make path optional
    try:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(script_dir, "home_assistant.txt")

            with open(output_file, "w") as f:
                f.write(message)

            response = f"✅ Saved to:\n{output_file}"
            await websocket.send(response)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Error: {str(e)}")


async def main():
    async with websockets.serve(
            handle_message,
            "localhost",
            8765,
            # These parameters prevent the "CLOSING/CLOSED state" error
            ping_interval=None,
            close_timeout=None
    ):
        print("🚀 WebSocket server running at ws://localhost:8765")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())