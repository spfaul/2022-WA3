import curses
import curses.ascii
from typing import Union
from .term_window import TerminalWindow
from .command_line import CommandLine
from core.commands import BasicCommandSet
from core.keyboard import KeyboardHandler

class MasterWindow:
    """
    Root window manager which houses and manages all ui components
    """    
    def __init__(self, logs, stdscr) -> None:
        self.logs = logs
        self.stdscr = stdscr
        self.running: bool = False
        self.size_y: int
        self.size_x: int
        self.size_y, self.size_x = stdscr.getmaxyx()
        self.term_wins: list[TerminalWindow] = [TerminalWindow(logs, stdscr.derwin(self.size_y-1, self.size_x, 1, 0), self.on_term_destroy, active=True)]
        self.setup_commands()
        self.current_active_term: TerminalWindow = self.term_wins[0]
        self.kbh: KeyboardHandler = KeyboardHandler(stdscr)

    def setup_commands(self) -> None:
        """
        Setting up command line UI and command backend 
        """
        self.command_line: CommandLine = CommandLine(self.logs, self.stdscr.derwin(1, self.size_x, 0, 0))
        self.command_line.inject(BasicCommandSet(self))

    def on_term_destroy(self, term: TerminalWindow) -> None:
        self.cycle_active_term()
        self.term_wins.remove(term)
        if len(self.term_wins) == 0:
            self.running = False

    def create_term_down(self, key: Union[bytes, None] = None) -> None:
        """
        Called in `vsplit` command to "split" a terminal vertically into 2. Creates a new TerminalWindow instance
        which occupies the bottom-half of the space of the current active terminal.
        The current active terminal is then resized to take up the top-part of the
        space and the newly created terminal is then made active.
        """
        start_y: int
        start_x: int
        size_y: int
        size_x: int
        start_y, start_x = self.current_active_term.real_win().getbegyx()
        size_y, size_x = self.current_active_term.real_win().getmaxyx()
        new_y: int = size_y//2
        self.current_active_term.resize(size_x, new_y)
        self.current_active_term.is_active = False
        self.current_active_term = TerminalWindow(self.logs, self.stdscr.derwin(size_y-new_y, size_x, start_y+new_y, start_x), self.on_term_destroy, active=True)
        # Reinvoke draw() to readjust cursor position of new terminal
        self.current_active_term.draw()
        # Add terminal window to update queue
        self.term_wins.append(self.current_active_term)

    def create_term_right(self, key: Union[bytes, None] = None) -> None:
        """
        Called in `hsplit` command to "split" a terminal horizontally into 2. Creates a new TerminalWindow instance
        which occupies the right-half of the space of the current active terminal.
        The current active terminal is then resized to take up the left-half of the
        space and the newly created terminal is then made active.
        """
        start_y: int
        start_x: int
        size_y: int
        size_x: int
        start_y, start_x = self.current_active_term.real_win().getbegyx()
        size_y, size_x = self.current_active_term.real_win().getmaxyx()
        new_x: int = size_x//2
        self.current_active_term.resize(new_x, size_y)
        self.current_active_term.is_active = False
        self.current_active_term = TerminalWindow(self.logs, self.stdscr.derwin(size_y, size_x-new_x, start_y, start_x+new_x), self.on_term_destroy, active=True)
        # Reinvoke draw() to readjust cursor position of new terminal
        self.current_active_term.draw()
        # Add terminal window to update queue
        self.term_wins.append(self.current_active_term)

    def cycle_active_term(self, key: Union[bytes, int, None] = None) -> None:
        """
        Cycles the active terminal to the next terminal according 
        to the order of `term_wins`. Alternatively, next active terminal
        can be specified by passing its index in `term_wins` as `param: key`
        """
        self.current_active_term.is_active = False
        idx_active: int = self.term_wins.index(self.current_active_term)
        if isinstance(key, int) and 0 <= key <= len(self.term_wins)-1:
            idx_active = key
        elif idx_active == len(self.term_wins)-1:
            idx_active = 0
        else:
            idx_active += 1
        self.current_active_term = self.term_wins[idx_active]
        self.current_active_term.is_active = True
        self.current_active_term.draw()
        self.current_active_term.draw()

    def init_kb(self) -> None:
        """
        Setup listeners and callbacks to different keystrokes
        """
        self.kbh.on("*", self.on_key) # Will fire upon any keystroke
        self.kbh.on("\x00", self.create_term_right) # Ctrl-2
        self.kbh.on("\x1b", self.create_term_down) # Ctrl-3
        self.kbh.on("\x1c", self.cycle_active_term) # Ctrl-4
        self.kbh.on("\x1d", self.focus_command_line) # Ctrl-5

    def focus_command_line(self, key: bytes) -> None:
        """
        Allow user to type into command line and execute commands.
        NOTE: This WILL block the main thread and pause updating
        of terminals. 
        """
        self.command_line.interact()
        self.current_active_term.draw()
        
    def on_key(self, key: bytes) -> None:
        """
        Called upon any keystroke. Essentially forwards keys from 
        stdin of main thread to pty of current active terminal
        """
        self.logs.info(f"Key Pressed: \"{key}\"")
        if key in (b"\x00", b"\x1b", b"\x1c", b"\x1d"):
            return
        self.current_active_term.term.send(key)
        self.current_active_term.update()
        
    def run(self) -> None:
        """
        Main event loop
        """
        self.running = True
        self.init_kb()
        self.stdscr.erase()
        while self.running:
            for term in self.term_wins:
                term.update()
            self.kbh.getch()
