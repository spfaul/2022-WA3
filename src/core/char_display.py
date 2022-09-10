import curses.ascii
from typing import Tuple, List

class Cursor:
    """
    Virtual cursor to facilitate drawing in `CharDisplay`
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set_pos(self, x, y):
        self.x, self.y = x, y

    def get_pos(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"<Cursor x={self.x} y={self.y}>"

class CharCell:
    """
    The smallest unit of each `CharDisplay`, each emulating a single
    cell on a terminal display.
    """
    def __init__(self, char=""):
        self.data = char
    def __repr__(self):
        return self.data

class CharDisplay:
    """
    Backend terminal drawing and manipulation before being used duplicated to actual UI.
    This class exists because performing controlled manipulation of terminal cells
    to the UI itself in realtime would not only be extremely tedious, but also painfully slow.
    """
    def __init__(self, logs, size):
        self.logs = logs
        self.size: Tuple[int, int] = size
        self.curs: Cursor = Cursor(0, 0)
        self.buffer: List[List[CharCell]] = [[CharCell() for _ in range(self.size[0])] for _ in range(self.size[1])]

    def resize(self, new_x: int, new_y: int) -> None:
        """
        Resize display, usually called as a result of `vsplit` or `hsplit`
        """
        # Remove excess rows if neccesary 
        if self.size[1] > new_y:
            new = self.buffer[:self.curs.y+1] # rows before and including cursor row
            if len(new) > new_y:
                self.buffer = new[-new_y:] # Take last <new_y> rows from <new> if have excess
            else:
                self.buffer = self.buffer[-new_y:] # Take last <new_y> rows from entire buffer
        # Remove excess cells from rows if neccesary
        if self.size[0] > new_x:
            for y in range(len(self.buffer)):
                self.buffer[y] = self.buffer[y][:new_x] # row = first <new_x> cells
        # Adjust cursor if outside new boundaries
        if self.curs.x >= new_x:
            self.curs.x = new_x-1
        if self.curs.y >= new_y:
            self.curs.y = new_y-1
        # Set new display size
        self.size = (new_x, new_y)

    def write(self, text: str) -> None:
        """
        Insert text into CharDisplay at cursor position
        """
        for c in text:
            try:
                # NOTE: IndexOutOfBounds errors may occur here due to resize lag
                self.buffer[self.curs.y][self.curs.x].data = c 
            except IndexError:
                self.logs.error(f"Error while writing to CharDisplay, {self.curs} {self.buffer}")
                self.curs.y = 0
                self.curs.x = 0
            self.advance_cursor()

    def newline(self) -> None:
        """
        Handle insertion of newline ("\n")
        """
        if self.curs.y == self.size[1]-1:
            self.buffer.pop(0)
            self.buffer.append([CharCell() for _ in range(self.size[0])])
            return
        self.curs.y += 1

    def advance_cursor(self) -> None:
        """ Move cursor forward by 1 cell """
        if self.curs.x >= self.size[0]-1:
            self.curs.x = 0
            self.newline()
            return
        self.curs.x += 1

    def erase_all(self) -> None:
        self.erase((0,0), (self.size[0]-1, self.size[1]-1))

    def erase_all_to_curs(self) -> None:
        self.erase((0,0), self.curs.get_pos())

    def erase_all_from_curs(self) -> None:
        self.erase(self.curs.get_pos(), (self.size[0]-1, self.size[1]-1))

    def erase_inline_from_curs(self) -> None:
        self.erase((self.curs.x, self.curs.y), (self.size[0]-1, self.curs.y))
    
    def erase(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """ Erase cells from specified start cell to end cell in a downwards and rightwards fashion """
        lines = self.buffer[start[1]:end[1]+1]
        if not len(lines):
            return
        lines[0] = lines[0][start[0]:]
        lines[-1] = lines[-1][:end[0]+1]
        for line in lines:
            for cell in line:
                cell.data = ""