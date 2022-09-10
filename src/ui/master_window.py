"""
Implementation of the MasterWindow class - the base screen which all ui will be drawn upon
"""

import curses
import curses.ascii
from .term_window import TerminalWindow
from .command_line import CommandLine
from core.commands import BasicCommandSet
from .keyboard import KeyboardHandler

class MasterWindow:
    def __init__(self, logs, stdscr):
        self.logs = logs
        self.stdscr = stdscr
        self.running = False
        self.size_y, self.size_x = stdscr.getmaxyx()
        self.term_wins = [TerminalWindow(logs, stdscr.derwin(self.size_y-1, self.size_x, 1, 0), self.on_term_destroy, active=True)]
        self.setup_commands()
        self.current_active_term = self.term_wins[0]
        self.kbh = KeyboardHandler(stdscr)

    def setup_commands(self):
        self.command_line = CommandLine(self.logs, self.stdscr.derwin(1, self.size_x, 0, 0))
        self.command_line.inject(BasicCommandSet(self))

    def on_term_destroy(self, term):
        self.cycle_active_term()
        self.term_wins.remove(term)
        if len(self.term_wins) == 0:
            self.running = False

    def create_term_down(self, key=None):
        start_y, start_x = self.current_active_term.real_win().getbegyx()
        size_y, size_x = self.current_active_term.real_win().getmaxyx()
        new_y = size_y//2
        self.current_active_term.resize(size_x, new_y)
        self.current_active_term.is_active = False
        new_term = TerminalWindow(self.logs, self.stdscr.derwin(size_y-new_y, size_x, start_y+new_y, start_x), self.on_term_destroy, active=True)
        self.current_active_term = new_term
        self.current_active_term.draw()
        self.term_wins.append(new_term)

    def create_term_right(self, key=None):
        start_y, start_x = self.current_active_term.real_win().getbegyx()
        size_y, size_x = self.current_active_term.real_win().getmaxyx()
        new_x = size_x//2
        self.current_active_term.resize(new_x, size_y)
        self.current_active_term.is_active = False
        new_term = TerminalWindow(self.logs, self.stdscr.derwin(size_y, size_x-new_x, start_y, start_x+new_x), self.on_term_destroy, active=True)
        self.current_active_term = new_term
        self.current_active_term.draw()
        self.term_wins.append(new_term)

    def cycle_active_term(self, key=None):            
        self.current_active_term.is_active = False
        idx_active = self.term_wins.index(self.current_active_term)
        if isinstance(key, int) and 0 <= key <= len(self.term_wins)-1:
            idx_active = key
        elif idx_active == len(self.term_wins)-1:
            idx_active = 0
        else:
            idx_active += 1
        self.current_active_term = self.term_wins[idx_active]
        self.current_active_term.is_active = True
        self.current_active_term.draw()

    def init_kb(self):
        self.kbh.on("*", self.on_key)
        self.kbh.on("\x00", self.create_term_right)
        self.kbh.on("\x1b", self.create_term_down)
        self.kbh.on("\x1c", self.cycle_active_term)
        self.kbh.on("\x1d", self.focus_command_line)

    def focus_command_line(self, key=None):
        self.command_line.interact()
        self.current_active_term.draw()
        
    def on_key(self, key):
        self.logs.info(f"key is {key}")
        self.current_active_term.term.send(key)
        self.current_active_term.update()
        
    def run(self):
        self.running = True
        self.init_kb()
        self.stdscr.erase()
        while self.running:
            for term in self.term_wins:
                term.update()
            self.kbh.getch()
