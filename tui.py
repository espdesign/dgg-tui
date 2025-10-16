import asyncio
import curses
import json
import websockets
from dotenv import load_dotenv
import os

load_dotenv()
DGG_SID = os.getenv("DGG_SID")
DGG_REMEMBERME = os.getenv("DGG_REMEMBERME")


async def chat_client(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    # Get screen dimensions
    height, width = stdscr.getmaxyx()

    # Create windows
    messages_win = curses.newwin(height - 3, width, 0, 0)
    input_win = curses.newwin(3, width, height - 3, 0)

    messages_win.scrollok(True)
    input_win.keypad(True)
    input_win.nodelay(True)

    messages = []

    async def receive_messages(websocket):
        while True:
            try:
                message = await websocket.recv()
                event_name, payload = message.split(" ", 1)
                event_name = event_name.upper()
                try:
                    data = json.loads(payload)
                    if event_name == "MSG":
                        messages.append(f"{data['nick']}: {data['data']}")
                    elif event_name == "NAMES":
                        pass
                        # messages.append(
                        #     f"Connected users: {', '.join([user['nick'] for user in data['users']])}"
                        # )
                    else:
                        pass
                        # messages.append(message)
                except json.JSONDecodeError:
                    messages.append(message)

                draw_messages()
            except websockets.exceptions.ConnectionClosed:
                messages.append("Connection closed.")
                draw_messages()
                break

    def draw_messages():
        messages_win.clear()
        max_messages = height - 4
        for i, msg in enumerate(messages[-max_messages:]):
            messages_win.addstr(i, 0, msg)
        messages_win.refresh()

    def draw_input(input_text):
        input_win.clear()
        input_win.border()
        input_win.addstr(1, 1, "Message: " + input_text)
        input_win.refresh()

    async def send_messages(websocket, receive_task):
        input_text = ""
        while True:
            draw_input(input_text)
            try:
                key = await asyncio.to_thread(input_win.getch)
            except asyncio.CancelledError:
                break

            if key != -1:
                if key == curses.KEY_ENTER or key == 10 or key == 13:
                    if input_text:
                        await websocket.send(f"MSG {json.dumps({'data': input_text})}")
                        input_text = ""
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_text = input_text[:-1]
                elif key == 27:  # ESC key
                    receive_task.cancel()
                    break
                elif 32 <= key <= 126:
                    input_text += chr(key)

            await asyncio.sleep(0.01)

    uri = "wss://chat.destiny.gg/ws"
    headers = {"Cookie": f"sid={DGG_SID}; rememberme={DGG_REMEMBERME}"}
    try:
        async with websockets.connect(
            uri, additional_headers=headers, ping_interval=None
        ) as websocket:
            messages.append(f"Connected to {uri}")
            draw_messages()

            receive_task = asyncio.create_task(receive_messages(websocket))
            send_task = asyncio.create_task(send_messages(websocket, receive_task))

            await asyncio.gather(receive_task, send_task)

    except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError) as e:
        messages.append(f"Failed to connect to {uri}: {e}")
        draw_messages()
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(curses.wrapper(chat_client))
    except KeyboardInterrupt:
        pass
