"""
Terminal Emulator UI - each TerminalWindow object spins up a single process
"""

import re
import select
from dataclasses import dataclass
from core.esc_code import EscCodeHandler
from core.termproc import TerminalProcess
from core.char_display import CharDisplay, CharCell
from .boxed import Boxed


class TerminalWindow(Boxed):
    def __init__(self, logs, win):
        super().__init__(win)
        self.logs = logs
        max_y, max_x = self._win.getmaxyx()
        self.term = TerminalProcess()
        self.char_disp = CharDisplay((max_x, max_y))
        self.esc_handler = EscCodeHandler(self.logs, self.char_disp)
        self.setup_esc()
        self.__line = ""

    def setup_esc(self):
        self.esc_handler.on("A", self.move_curs_up)
        self.esc_handler.on("B", self.move_curs_down)
        self.esc_handler.on("C", self.move_curs_right)
        self.esc_handler.on("D", self.move_curs_left)

    def move_curs_up(self, disp, lines):
        disp.curs.y -= int(lines)
        if disp.curs.y < 0:
            disp.curs.y = 0

    def move_curs_down(self, disp, lines):
        disp.curs.y += int(lines)
        if disp.curs.y > disp.size[1]-1:
            disp.curs.y = disp.size[1] - 1

    def move_curs_right(self, disp, cols):
        disp.curs.x += int(cols)
        if disp.curs.x > disp.size[0]-1:
            disp.curs.x = disp.size[0] - 1

    def move_curs_left(self, disp, cols):
        disp.curs.x -= int(cols)
        if disp.curs.x < 0:
            disp.curs.x = 0

    def draw(self):
        self._win.erase()
        for y, row in enumerate(self.char_disp.buffer):
            for x, cell in enumerate(row):
                if cell.data:
                    self._win.addch(y, x, cell.data)
        self._win.refresh()

    __line = ""
    def _parse(self, chunk):
        while chunk:
            c = chunk[0]
            if c == "\n":
                self.char_disp.write(self.__line)
                self.char_disp.newline()
                self.__line = ""
            elif c == "\x1b":
                new_chunk = self.esc_handler.handle_head(chunk)
                if new_chunk is None:
                    self.char_disp.write(self.__line)
                    self.__line = c
                    return
                chunk = new_chunk
                continue
            elif c == "\r":
                self.char_disp.write(self.__line)
                self.char_disp.curs.x = 0
                self.__line = ""
            else:
                self.__line += c
            chunk = chunk[1:]

        if len(self.__line):
            self.char_disp.write(self.__line)
        self.__line = ""

    def update(self):
        for buff in [self.term.stdout, self.term.stderr]:
            chunk = self.term.read(buff, 4096)
            if chunk:
                self.logs.info(repr(chunk))
                self._parse(chunk)
            self.draw()

    