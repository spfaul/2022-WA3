"""
Implementation of the MasterWindow class - the base screen which all ui will be drawn upon
"""

import curses
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
        self.kbh.on("*", self.asd)

    def asd(self, key):
        self.logs.info(f"key is {key}/{chr(key)}")
        self.term_win.term.send(chr(key).encode("utf8"))
        # self.term_win.term.send("a\n".encode("utf8"))
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

