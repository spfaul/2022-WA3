"""
Terminal Emulator UI - each TerminalWindow object spins up a single process
"""

import re
from core.esc_code import EscCodeHandler
from core.termproc import TerminalProcess
from .boxed import Boxed

class TerminalWindow(Boxed):
    def __init__(self, logs, win):
        super().__init__(win)
        self.logs = logs
        self.max_y, self.max_x = self._win.getmaxyx()
        self.term = TerminalProcess()
        self.esc_handler = EscCodeHandler(self.logs)
        self.term.resize(10,10)
        self.buffer_lines = [[]]

    def addstr(self, s):
        self._win.addstr(s)

    def draw(self):
        self._win.erase()
        visible_lines = self.buffer_lines[-int(self.max_y-1):]

        max_lines = self.max_y-1
        for line in visible_lines:
            x_count = 0
            for chunk in line:
                x_count += len(chunk)
                if x_count > self.max_x:
                    max_lines -= 1
                    x_count = self.max_x - x_count
                    
        visible_lines = visible_lines[-max_lines:]
        for line in visible_lines:
            for chunk in line:
                self.addstr(chunk)
            self.addstr("\n")
        self._win.refresh()

    def _parse(self, chunk):
        line = ""
        while chunk:
            c = chunk[0]
            if c == "\n":
                self.buffer_lines[-1].append(line)
                self.buffer_lines.append([])
                line = ""
            elif c == "\x1b":
                chunk = self.esc_handler.handle_head(chunk)
                continue
            elif c == "\r":
                pass
            else:
                line += c
            chunk = chunk[1:]
        if len(line):
            self.buffer_lines[-1].append(line)
                
    def update(self):
        chunk = self.term.read(4096)
        if chunk:
            self._parse(chunk)
        self.draw()