class KeyboardHandler:
    def __init__(self, win):
        self.win = win
        self.keymap = {}
        
    def listen(self, key_list, func):
        for key in key_list:
            if key not in self.keymap:
                self.keymap[key] = [func]
            else:
                self.keymap[key].append(func)

    def getch(self):
        key = self.win.getch()
        if key != -1: # No key pressed
            self.dispatch(key)

    def dispatch(self, key):
        if "*" in self.keymap:
            for callback in self.keymap["*"]:
                callback(key)
        if key in self.keymap:
            for callback in self.keymap[key]:
                callback(key)