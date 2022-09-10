import sys
import os
import select
import termios
import tty

class KeyboardHandler:
    def __init__(self, win):
        self.win = win
        self.keymap = {}
        self.stdinfd = sys.stdin.fileno()
        self.old_stdin_attrs = termios.tcgetattr(self.stdinfd)
        tty.setraw(self.stdinfd)

    def cleanup(self):
        termios.tcsetattr(self.stdinfd, termios.TCSADRAIN, self.old_stdin_attrs)
        
    def on(self, key_list, func):
        for key in key_list:
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            if key not in self.keymap:
                self.keymap[key] = [func]
            else:
                self.keymap[key].append(func)

    def getch(self):
        i, _, _ = select.select([sys.stdin],[],[], 0)
        if i == [sys.stdin]:
            key = os.read(self.stdinfd, 1024)
            self.dispatch(key)

    def dispatch(self, key):
        if "*" in self.keymap:
            for callback in self.keymap["*"]:
                callback(key)
        if isinstance(key, bytes):
            hashed_key = key.decode("utf-8")
        if hashed_key in self.keymap:
            for callback in self.keymap[hashed_key]:
                callback(key)