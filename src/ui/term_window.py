import re
import curses
import select
from typing import Callable
from core.esc_code import EscCodeHandler
from core.termproc import TerminalProcess
from core.char_display import CharDisplay, CharCell
from .boxed import Boxed

class TerminalWindow(Boxed):
    """
    Terminal emulator UI 
    """
    def __init__(self, logs, win, on_destroy: Callable[[], None], active: bool = False) -> None:
        super().__init__(win)
        self.logs = logs
        self.on_destroy: Callable[[], None] = on_destroy
        max_y, max_x = self._win.getmaxyx()
        self.term: TerminalProcess = TerminalProcess()
        self.term.resize(max_x, max_y)
        self.char_disp: CharDisplay = CharDisplay(logs, (max_x, max_y))
        self.esc_handler: EscCodeHandler = EscCodeHandler(self.logs, self.char_disp)
        self.is_active: bool = active
        self.setup_esc()
        self.box()

    def resize(self, new_x: int, new_y: int) -> None:
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
        self.term.resize(new_x-2, new_y-2)
        self.char_disp.resize(new_x-2, new_y-2)
        self.draw()
        
    def refresh_curs(self):
        """ Update cursor position to emulated backend cursor position """
        self._win.move(self.char_disp.curs.y, self.char_disp.curs.x)

    def setup_esc(self):
        """ 
        Setup listeners to handle corresponding escape code encounters.
        See https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797 for
        more information about different UNIX ANSI escape codes
        """
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

    def move_curs_horizontal(self, disp: CharDisplay, cols: str):
        cols: int = int(cols)
        if not cols:
            cols = 1
        disp.curs.x = cols - 1

    def move_curs_vertical(self, disp: CharDisplay, lines: str):
        lines: int = int(lines)
        if not lines:
            lines: int = 1
        disp.curs.y = lines - 1

    def move_curs_home(self, disp: CharDisplay, lines: int = 1, cols: int = 1):
        if lines == "0":
            lines: int = 1
        if cols == "0":
            cols: int = 1
        disp.curs.set_pos(int(cols)-1, int(lines)-1)

    def backspace_char(self, disp: CharDisplay, code: str):
        cols: int = int(code)
        if cols == 0:
            cols = 1
        # Erase `cols` number of cells after cursor position
        for cell in disp.buffer[disp.curs.y][disp.curs.x:disp.curs.x+cols]:
            cell.data = ""
        self.draw()
        
    def del_char(self, disp: CharDisplay, code: str):
        line: list[CharCell] = disp.buffer[disp.curs.y]
        cols: int = int(code)
        if not cols:
            cols = 1
        if cols + disp.curs.x > disp.size[0] - 1: # Attempted deleting past line size, Invalid delete
            self.logs.error(f"Invalid delete escape code, tried {cols} when max is {disp.size[0]}")
            return
        # row = <row before curs> + <row after last deleted cell> + <replacement cells for deleted cells> 
        disp.buffer[disp.curs.y] = line[:disp.curs.x] + line[disp.curs.x+cols:] + [CharCell() for _ in range(cols)]
        self.draw()

    def erase_disp(self, disp: CharDisplay, code: str):
        if code == "0":
            disp.erase_all_to_curs()
        elif code == "1":
            disp.erase_all_from_curs()
        elif code == "2":
            disp.erase_all()

    def erase_inline(self, disp: CharDisplay, code: str):
        if code == "0":
            disp.erase_inline_from_curs()

    def move_curs_up(self, disp: CharDisplay, lines: str):
        if lines == "0":
            lines: int = 1
        disp.curs.y = max(0, disp.curs.y-int(lines))
        self.refresh_curs()
    
    def move_curs_down(self, disp: CharDisplay, lines: str):
        if lines == "0":
            lines: int = 1
        disp.curs.y = min(disp.size[1]-1, disp.curs.y+int(lines))
        self.refresh_curs()

    def move_curs_right(self, disp: CharDisplay, cols: str):
        if cols == "0":
            cols: int = 1
        disp.curs.x = min(disp.size[0]-1, disp.curs.x+int(cols))
        self.refresh_curs()

    def move_curs_left(self, disp: CharDisplay, cols: str):
        if cols == "0":            
            cols: int = 1
        disp.curs.x = max(0, disp.curs.x-int(cols))
        self.refresh_curs()

    def draw(self) -> None:
        """
        Construction of frontend terminal display
        """
        if self.is_active:
            curses.curs_set(2) # Set cursor to blinking
        else:
            curses.curs_set(0) # Hide cursor
        self.box()
        self._win.erase()
        for y, row in enumerate(self.char_disp.buffer):
            for x, cell in enumerate(row):
                if cell.data:
                    self._win.addch(y, x, cell.data)
        self.refresh_curs()
        self._win.refresh()

    def _parse(self, chunk: str) -> None:
        line = ""
        while chunk:
            c: str = chunk[0]
            if c == "\n": # newline
                self.char_disp.write(line)
                self.char_disp.newline()
                line = ""
            elif c == "\x1b": # encountered potential escape code
                self.char_disp.write(line)            
                line = ""
                new_chunk = self.esc_handler.handle_head(chunk)
                if new_chunk is not None:
                    chunk = new_chunk
                    continue
            elif c == "\r": # return carriage
                self.char_disp.write(line)
                self.char_disp.curs.x = 0
                line = ""
            elif c == "\b": # backspace
                self.char_disp.write(line)
                self.move_curs_left(self.char_disp, 1)
                line = ""
            else:
                line += c
            # Prepare next character for parsing
            chunk = chunk[1:]
        # Write any leftover trailing data
        self.char_disp.write(line)

    def update(self) -> None:
        """
        Called every tick of event loop to update terminal window
        """
        # If terminal process ended, destroy ourselves
        if self.term.proc.poll() is not None:
            self.on_destroy(self)
        # Check stdout and stderr for new data
        for buff in [self.term.stdout, self.term.stderr]:
            chunk: str = self.term.read(buff, 4096)
            if chunk:
                self.logs.info(f"Chunk Received: {repr(chunk)}")
                self._parse(chunk)
                self.draw()