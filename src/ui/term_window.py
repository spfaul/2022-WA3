"""
Terminal Emulator UI - each TerminalWindow object spins up a single process
"""

import re
import curses
import select
from dataclasses import dataclass
from core.esc_code import EscCodeHandler
from core.termproc import TerminalProcess
from core.char_display import CharDisplay, CharCell
from .boxed import Boxed


class TerminalWindow(Boxed):
    def __init__(self, logs, win, on_destroy, active=False):
        super().__init__(win)
        self.logs = logs
        self.on_destroy = on_destroy
        max_y, max_x = self._win.getmaxyx()
        self.term = TerminalProcess()
        self.term.resize(max_x-2, max_y-2)
        self.char_disp = CharDisplay(logs, (max_x, max_y))
        self.esc_handler = EscCodeHandler(self.logs, self.char_disp)
        self.is_active = active
        self.setup_esc()
        self.box()
        self.__line = ""

    def resize(self, new_x, new_y):
        # Clear windows to prevent leftover characters
        self._real_win.erase()
        self._real_win.refresh()
        self._win.erase()
        self._win.refresh()
        # Redraw box
        self._real_win.resize(new_y, new_x)
        self.box()
        self._real_win.refresh()
        # Create new window instance and redraw
        start_y, start_x = self._real_win.getbegyx()
        self._win = self._real_win.derwin(new_y-2, new_x-2, 1, 1)
        self.term.resize(new_x-2-2, new_y-2-2)
        self.char_disp.resize(new_x-2, new_y-2)
        self.draw()
        
    def refresh_curs(self):
        self.logs.info(f"{self.char_disp.curs}, {self.char_disp.size}")
        self._win.move(self.char_disp.curs.y, self.char_disp.curs.x)

    def setup_esc(self):
        self.esc_handler.on("A", self.move_curs_up)
        self.esc_handler.on("B", self.move_curs_down)
        self.esc_handler.on("C", self.move_curs_right)
        self.esc_handler.on("D", self.move_curs_left)
        self.esc_handler.on("H", self.move_curs_home)
        self.esc_handler.on("d", self.move_curs_vertical)
        self.esc_handler.on("G", self.move_curs_horizontal)
        self.esc_handler.on("J", self.erase_disp)
        self.esc_handler.on("K", self.erase_inline)
        self.esc_handler.on("P", self.del_char)
        self.esc_handler.on("@", self.backspace_char)

    def move_curs_horizontal(self, disp, cols):
        cols = int(cols)
        if not cols:
            cols = 1
        disp.curs.x = cols - 1

    def move_curs_vertical(self, disp, lines):
        lines = int(lines)
        if not lines:
            lines = 1
        disp.curs.y = lines - 1

    def move_curs_home(self, disp, lines=1, cols=1):
        if lines == "0":
            lines = 1
        if cols == "0":
            cols = 1
        disp.curs.set_pos(int(cols)-1, int(lines)-1)

    def backspace_char(self, disp, code):
        cols = int(code)
        if cols == 0:
            cols = 1
        self.logs.info(disp.buffer[disp.curs.y])
        for cell in disp.buffer[disp.curs.y][disp.curs.x:disp.curs.x+cols]:
            cell.data = ""
        self.logs.info(disp.buffer[disp.curs.y])
        self.draw()
        
    def del_char(self, disp, code):
        line = disp.buffer[disp.curs.y]
        cols = int(code)
        if not cols:
            cols = 1
        if cols + disp.curs.x > disp.size[0] - 1:
            return
        self.logs.info(disp.buffer[disp.curs.y])
        disp.buffer[disp.curs.y] = line[:disp.curs.x] + line[disp.curs.x+cols:] + [CharCell() for _ in range(cols)]
        self.logs.info(disp.buffer[disp.curs.y])
        self.draw()

    def erase_disp(self, disp, code):
        if code == "0":
            disp.erase_all_to_curs()
        elif code == "1":
            disp.erase_all_from_curs()
        elif code == "2":
            disp.erase_all()

    def erase_inline(self, disp, code):
        if code == "0":
            disp.erase_inline_from_curs()

    def move_curs_up(self, disp, lines):
        if lines == "0":
            lines = 1
        disp.curs.y = max(0, disp.curs.y-int(lines))
    
    def move_curs_down(self, disp, lines):
        if lines == "0":
            lines = 1
        disp.curs.y = min(disp.size[1]-1, disp.curs.y+int(lines))

    def move_curs_right(self, disp, cols):
        if cols == "0":
            cols = 1
        disp.curs.x = min(disp.size[0]-1, disp.curs.x+int(cols))

    def move_curs_left(self, disp, cols):
        if cols == "0":            
            cols = 1
        disp.curs.x = max(0, disp.curs.x-int(cols))
        self.refresh_curs()

    def draw(self):
        if self.is_active:
            curses.curs_set(2)
        else:
            curses.curs_set(0)
        self.box()
        self._win.erase()
        for y, row in enumerate(self.char_disp.buffer):
            for x, cell in enumerate(row):
                if cell.data:
                    self._win.addch(y, x, cell.data)
        self.refresh_curs()
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
                self.char_disp.write(self.__line)            
                self.__line = ""
                new_chunk = self.esc_handler.handle_head(chunk)
                if new_chunk is not None:
                    chunk = new_chunk
                    continue
            elif c == "\r":
                self.char_disp.write(self.__line)
                self.char_disp.curs.x = 0
                self.__line = ""
            elif c == "\b":
                self.char_disp.write(self.__line)
                self.move_curs_left(self.char_disp, 1)
                self.__line = ""
            else:
                self.__line += c
            chunk = chunk[1:]

        self.char_disp.write(self.__line)
        self.__line = ""

    def update(self):
        if self.term.proc.poll() is not None:
            self.on_destroy(self)
        for buff in [self.term.stdout, self.term.stderr]:
            chunk = self.term.read(buff, 4096)
            if chunk:
                self.logs.info(repr(chunk))
                self._parse(chunk)
                self.draw()