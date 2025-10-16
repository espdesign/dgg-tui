import asyncio
import json
import websockets

class WebSocketClient:
    def __init__(self, uri, headers):
        self.uri = uri
        self.headers = headers
        self.websocket = None
        self.messages = []

    async def connect(self):
        try:
            self.websocket = await websockets.connect(
                self.uri, additional_headers=self.headers, ping_interval=None
            )
            self.messages.append(f"Connected to {self.uri}")
            return True
        except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError) as e:
            self.messages.append(f"Failed to connect to {self.uri}: {e}")
            return False

    async def receive_message(self):
        try:
            message = await self.websocket.recv()
            event_name, payload = message.split(" ", 1)
            event_name = event_name.upper()
            try:
                data = json.loads(payload)
                if event_name == "MSG":
                    self.messages.append(f"{data['nick']}: {data['data']}")
                elif event_name == "NAMES":
                    pass
                else:
                    pass
            except json.JSONDecodeError:
                self.messages.append(message)
        except websockets.exceptions.ConnectionClosed:
            self.messages.append("Connection closed.")

    async def send_message(self, message):
        await self.websocket.send(message)
