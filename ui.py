import curses
import textwrap

class TUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.stdscr.clear()
        self.stdscr.refresh()

        height, width = self.stdscr.getmaxyx()

        self.messages_win = curses.newwin(height - 3, width, 0, 0)
        self.input_win = curses.newwin(3, width, height - 3, 0)

        self.messages_win.scrollok(True)
        self.input_win.keypad(True)
        self.input_win.nodelay(True)

        self.init_colors()

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        self.color_map = {
            "USER": 1,
            "flair13": 2, # Tier 1
            "flair1": 3, # Tier 2
            "flair3": 4, # Tier 3
            "flair8": 5, # Tier 4
            "flair42": 6, # Tier 5 (Rainbow)
        }

    def draw_messages(self, messages):
        self.messages_win.erase()
        self.messages_win.border()
        height, width = self.messages_win.getmaxyx()
        max_messages = height
        y = 1
        for msg in messages[-max_messages:]:
            if y >= height -1:
                break
            if isinstance(msg, dict):
                color = self.color_map["USER"]
                is_rainbow = False
                if "features" in msg:
                    for flair in self.color_map.keys():
                        if flair in msg["features"]:
                            color = self.color_map[flair]
                            if color == 6:
                                is_rainbow = True
                            break
                
                nick = f"{msg['nick']}: "
                if is_rainbow:
                    rainbow_colors = [2, 3, 4, 5, 6, 7]
                    for i, char in enumerate(nick):
                        self.messages_win.addstr(y, 1 + i, char, curses.color_pair(rainbow_colors[i % len(rainbow_colors)]) | curses.A_BOLD)
                else:
                    self.messages_win.addstr(y, 1, nick, curses.color_pair(color) | curses.A_BOLD)
                
                lines = textwrap.wrap(msg["data"], width - len(nick) - 2)
                if not lines:
                    y += 1
                    continue

                self.messages_win.addstr(lines[0])
                for line in lines[1:]:
                    y += 1
                    if y >= height -1:
                        break
                    self.messages_win.addstr(y, len(nick) + 1, line)
                y += 1
            else:
                self.messages_win.addstr(y, 1, msg)
                y += 1
        self.messages_win.refresh()

    def draw_input(self, input_text):
        self.input_win.erase()
        self.input_win.border()
        self.input_win.addstr(1, 1, "Message: " + input_text)
        self.input_win.refresh()
