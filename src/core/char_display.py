import curses.ascii

class Cursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val

    def set_pos(self, x, y):
        self.x, self.y = x, y

    def get_pos(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"<Cursor x={self.x} y={self.y}>"

class CharCell:
    def __init__(self, char=""):
        self.data = char
    def __repr__(self):
        return self.data

class CharDisplay:
    def __init__(self, logs, size):
        self.logs = logs
        self.size = size
        self.curs = Cursor(0, 0)
        self.buffer = [[CharCell() for _ in range(self.size[0])] for _ in range(self.size[1])]

    def write(self, text):
        # self.logs.info(f"wrote {repr(text)}")
        for c in text:
            self.buffer[self.curs.y][self.curs.x].data = c
            self.advance_cursor()

    def newline(self):
        if self.curs.y == self.size[1]-1:
            self.buffer.pop(0)
            self.buffer.append([CharCell() for _ in range(self.size[0])])
            return
        self.curs.y += 1

    def advance_cursor(self):
        if self.curs.x >= self.size[0]-1:
            self.curs.x = 0
            self.newline()
            return
        self.curs.x += 1

    def erase_all(self):
        self.erase((0,0), (self.size[0]-1, self.size[1]-1))

    def erase_all_to_curs(self):
        self.erase((0,0), self.curs.get_pos())

    def erase_all_from_curs(self):
        self.erase(self.curs.get_pos(), (self.size[0]-1, self.size[1]-1))

    def erase_inline_from_curs(self):
        self.erase((self.curs.x, self.curs.y), (self.size[0]-1, self.curs.y))
    
    def erase(self, start, end):
        lines = self.buffer[start[1]:end[1]+1]
        if not len(lines):
            return
        lines[0] = lines[0][start[0]:]
        lines[-1] = lines[-1][:end[0]+1]
        for line in lines:
            for cell in line:
                cell.data = ""