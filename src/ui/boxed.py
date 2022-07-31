

class Boxed:
    def __init__(self, win):
        self._real_win = win
        max_y, max_x = win.getmaxyx()
        self._win = win.derwin(max_y-2, max_x-2, 1, 1)

    def box(self):
        self._real_win.box()
        self._real_win.refresh()

    def win(self):
        return self._win

    def real_win(self):
        return self._real_win