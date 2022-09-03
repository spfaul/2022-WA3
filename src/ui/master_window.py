"""
Implementation of the MasterWindow class - the base screen which all ui will be drawn upon
"""

import curses
import curses.ascii
from .term_window import TerminalWindow
from .keyboard import KeyboardHandler

class MasterWindow:
    def __init__(self, logs, stdscr):
        self.logs = logs
        self.stdscr = stdscr
        self.running = False
        self.size_y, self.size_x = stdscr.getmaxyx()
        self.term_win = TerminalWindow(logs, stdscr.derwin(self.size_y-1, self.size_x, 1, 0))
        self.kbh = KeyboardHandler(stdscr)

    def init_kb(self):
        self.kbh.on("*", self.on_key)
        # self.kbh.on([curses.KEY_LEFT], lambda key: self.term_win.term.send(b"\x1b[1D"))

    def on_key(self, key):
        self.logs.info(f"key is {key}/{chr(key)}")
        if key == curses.KEY_BACKSPACE:
            self.term_win.term.send(b"\b")
        # elif key == curses.KEY_LEFT:
            # self.logs.info(self.term_win.char_disp.curs.x)
            # self.term_win.move_curs_left(self.term_win.char_disp, 1)
        else:
            self.term_win.term.send(chr(key).encode("utf8"))
        self.term_win.update()
        self.stdscr.refresh()
        
    def run(self):
        self.running = True
        self.init_kb()
        self.stdscr.erase()
        self.term_win.box()
        while self.running:
            self.term_win.update()
            self.kbh.getch()            
