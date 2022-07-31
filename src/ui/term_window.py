"""
Terminal Emulator UI - each TerminalWindow object spins up a single process
"""

from .boxed import Boxed

class TerminalWindow(Boxed):
    def __init__(self, win):
        super().__init__(win)

    def addstr(self, s):
        self._win.addstr(s)
        
        