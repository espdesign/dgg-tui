import curses

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

    def draw_messages(self, messages):
        self.messages_win.erase()
        self.messages_win.border()
        height, _ = self.messages_win.getmaxyx()
        max_messages = height
        for i, msg in enumerate(messages[-max_messages:]):
            self.messages_win.addstr(i, 1, msg)
        self.messages_win.refresh()

    def draw_input(self, input_text):
        self.input_win.erase()
        self.input_win.border()
        self.input_win.addstr(1, 1, "Message: " + input_text)
        self.input_win.refresh()
