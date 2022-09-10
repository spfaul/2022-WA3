import curses.textpad
from typing import Union
from core.commands import DefaultCommandSet

class CommandLine(curses.textpad.Textbox):
    """
    Editable Command Line UI, basically a glorified textbox
    """
    def __init__(self, logs, win) -> None:
        self.logs = logs
        self._real_win = win
        self.prompt: str = "> "
        super().__init__(win.derwin(0, len(self.prompt)))
        self.command_set: DefaultCommandSet = DefaultCommandSet()

    def clear(self) -> None:
        """ Clear editable area """
        self.win.erase()
        self.win.refresh()

    def interact(self) -> None:
        """ Start interactable editing of command line for 1 command """
        self.clear()
        self._real_win.addstr(0, 0, self.prompt)
        self._real_win.refresh()
        contents: str = self.edit().strip()
        self.clear()
        output: Union[str, None] = self.command_set.process(contents)
        if output:
            self.win.addstr(output)
            self.win.refresh()

    def inject(self, command_set: DefaultCommandSet) -> None:
        """ Dependency injection of different command sets for flexibility and maintainability """
        self.command_set = command_set