class Cursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"<Cursor x={self.x} y={self.y}>"

class CharCell:
    def __init__(self, char=""):
        self.data = char
    def __repr__(self):
        return self.data

class CharDisplay:
    def __init__(self, size):
        self.size = size
        self.curs = Cursor(0, 0)
        self.buffer = [[CharCell() for _ in range(self.size[0])] for _ in range(self.size[1])]

    def write(self, text):
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

if __name__ == "__main__":
    d = CharDisplay()
    d.write("hihihi")
    d.newline()
    d.write("asdasd")
    print(d.buffer)