"""
Terminal Emulator UI - each TerminalWindow object spins up a single process
"""

from core.termproc import TerminalProcess
from .boxed import Boxed

class TerminalWindow(Boxed):
    def __init__(self, logs, win):
        super().__init__(win)
        self.logs = logs
        self.max_y, self.max_x = self._win.getmaxyx()
        self.term = TerminalProcess()
        self.term.resize(self.max_y, self.max_x)
        self.buffer_lines = [[]]

    def addstr(self, s):
        self._win.addstr(s)

    def draw(self):
        self._win.erase()
        visible_lines = self.buffer_lines[-int(self.max_y*3/4):]
        for line in visible_lines:
            for chunk in line:
                self.addstr(chunk)
            self.addstr("\n")
        self._win.refresh()

    def _parse(self, chunk):
        line = ""
        for c in chunk:
            if c == "\n":
                self.buffer_lines[-1].append(line)
                self.buffer_lines.append([])
                line = ""
            elif c == "\r":
                pass
            else:
                line += c
        self.buffer_lines[-1].append(line)
                
    def update(self):
        chunk = self.term.read(4096)
        if chunk:
            self._parse(chunk)
        self.draw()

        