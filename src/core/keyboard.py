import sys
import os
import select
import termios
import tty
from typing import Union, Callable

class KeyboardHandler:
    """
    Main Keyboard dispatcher - grabs keystrokes and distributes them to attached listeners
    """
    def __init__(self, win) -> None:
        self.win = win
        self.keymap = {}
        # Make stdin of main thread non-blocking 
        self.stdinfd = sys.stdin.fileno()
        self.old_stdin_attrs = termios.tcgetattr(self.stdinfd)
        tty.setraw(self.stdinfd)
        
    def on(self, key_list: Union[str, bytes], func: Callable[[bytes], None]) -> None:
        """
        Attach listeners to keystroke(s). Should be called prior to getch() to avoid loss of keystrokes
        """
        for key in key_list:
            # bytestrings get hashed into ints, so we store them as their string counterparts for keys for our dict
            if isinstance(key, bytes):
                key = key.decode("utf-8")
                
            if key not in self.keymap:
                self.keymap[key] = [func]
            else:
                self.keymap[key].append(func)

    def getch(self):
        """
        Hacky-way to Grab keystrokes from main thread stdin.
        Builtin curses getch() method returns keys unreliabily,
        so this is our workaround. Only works because we made
        stdin non-blocking in __init__().
        """
        i, _, _ = select.select([sys.stdin],[],[], 0) # Select syscall to check if theres data available in stdin
        if i == [sys.stdin]:
            # Data present, read and dispatch
            key = os.read(self.stdinfd, 1024)
            self.dispatch(key)

    def dispatch(self, key):
        """
        Inform listeners of keypress
        """
        if "*" in self.keymap:
            for callback in self.keymap["*"]:
                callback(key)
        if isinstance(key, bytes):
            hashed_key = key.decode("utf-8")
        if hashed_key in self.keymap:
            for callback in self.keymap[hashed_key]:
                callback(key)