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
        self.term_win = TerminalWindow(logs, stdscr.derwin(self.size_y, self.size_x, 0, 0))
        self.kbh = KeyboardHandler(stdscr)

    def init_kb(self):
        self.kbh.on("*", self.on_key)
        self.kbh.on([curses.KEY_BACKSPACE], lambda key: self.term_win.term.send(b"\b"))
        self.kbh.on([curses.KEY_LEFT], lambda key: self.term_win.term.send(b"\x1b[D"))
        self.kbh.on([curses.KEY_RIGHT], lambda key: self.term_win.term.send(b"\x1b[C"))
        self.kbh.on([curses.KEY_UP], lambda key: self.term_win.term.send(b"\x1b[A"))
        self.kbh.on([curses.KEY_DOWN], lambda key: self.term_win.term.send(b"\x1b[B"))
        self.kbh.on([curses.KEY_RESIZE], lambda key: self.resize())

    def resize(self):
        pass
        
    def on_key(self, key):
        self.logs.info(f"key is {key}/{chr(key)}")
        SPECIAL_KEYS = [curses.KEY_BACKSPACE, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_DC]
        if key not in SPECIAL_KEYS and curses.ascii.isascii(key):
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
