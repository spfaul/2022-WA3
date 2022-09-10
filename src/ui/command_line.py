import curses.textpad
from core.commands import DefaultCommandSet

class CommandLine(curses.textpad.Textbox):
    def __init__(self, logs, win):
        self.logs = logs
        self._real_win = win
        self.prompt = "> "
        super().__init__(win.derwin(0, len(self.prompt)))
        self.command_set = DefaultCommandSet()

    def clear(self):
        self.win.erase()
        self.win.refresh()

    def interact(self):
        self.clear()
        self._real_win.addstr(0, 0, self.prompt)
        self._real_win.refresh()
        contents = self.edit().strip()
        self.clear()
        output = self.command_set.process(contents)
        if output:
            self.win.addstr(output)
            self.win.refresh()

    def inject(self, command_set):
        self.command_set = command_set