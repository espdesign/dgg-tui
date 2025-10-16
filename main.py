import asyncio
import curses
import json
from config import DGG_SID, DGG_REMEMBERME
from ui import TUI
from client import WebSocketClient

async def main(stdscr):
    tui = TUI(stdscr)
    uri = "wss://chat.destiny.gg/ws"
    headers = {"Cookie": f"sid={DGG_SID}; rememberme={DGG_REMEMBERME}"}
    client = WebSocketClient(uri, headers)

    if not await client.connect():
        tui.draw_messages(client.messages)
        await asyncio.sleep(5)
        return

    tui.draw_messages(client.messages)

    async def receive_and_draw():
        while True:
            await client.receive_message()
            tui.draw_messages(client.messages)
            await asyncio.sleep(0.1)

    async def handle_input():
        input_text = ""
        while True:
            tui.draw_input(input_text)
            try:
                key = await asyncio.to_thread(tui.input_win.getch)
            except asyncio.CancelledError:
                break

            if key != -1:
                if key == curses.KEY_ENTER or key == 10 or key == 13:
                    if input_text:
                        await client.send_message(f"MSG {json.dumps({'data': input_text})}")
                        input_text = ""
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_text = input_text[:-1]
                elif key == 27:  # ESC key
                    try:
                        key2 = await asyncio.to_thread(tui.input_win.getch)
                        if key2 == -1:
                            receive_task.cancel()
                            break
                    except asyncio.CancelledError:
                        break
                elif 32 <= key <= 126:
                    input_text += chr(key)
            
            await asyncio.sleep(0.01)

    receive_task = asyncio.create_task(receive_and_draw())
    input_task = asyncio.create_task(handle_input())

    try:
        await asyncio.gather(receive_task, input_task)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))
