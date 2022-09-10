import shlex
import sys
from typing import Callable, List

class DefaultCommandSet:
    """
    Base command set of which all command sets
    inherit from. Implements basic methods which
    are required for usage in `CommandLine` component
    """
    def __init__(self):
        self.command_map: dict[str, Callable[[], str]] = {}

    def command_not_found(self, args):
        return f"Unknown command {args[0]}, try: \"help\""

    def add_command(self, *funcs: List[Callable[[], str]]) -> None:
        for func in funcs:
            self.command_map[func.__name__] = func

    def process(self, text: str) -> str:
        """
        Tokenize and Parse command line input similar how
        you would for actual terminal command line arguments.
        Call respective command (if any) and return output.
        """
        tokens: List[str] = shlex.split(text)
        if not len(tokens):
            return
        if tokens[0] in self.command_map:
            return self.command_map[tokens[0]](tokens[1:])
        else:
            return self.command_not_found(tokens)

class BasicCommandSet(DefaultCommandSet):
    """
    Basic command set implementation
    """
    def __init__(self, master_win) -> None:
        super().__init__()
        self.root = master_win
        self.add_command(
            self.quit,
            self.hsplit,
            self.vsplit,
            self.help,
            self.cycle
        )
            
    def quit(self, args: List[str]) -> None:
        self.root.running = False

    def hsplit(self, args: List[str]) -> str:
        self.root.create_term_right()
        return f"Term split successfully. There are {len(self.root.term_wins)} active sessions."

    def vsplit(self, args: List[str]) -> str:
        self.root.create_term_down()
        return f"Term split successfully. There are {len(self.root.term_wins)} active sessions."

    def help(self, args: List[str]) -> str:
        all_commands: str = ", ".join(list(self.command_map.keys()))
        return f"Available Commands: {all_commands}"

    def cycle(self, args: List[str]) -> str:
        if len(args):
            cycle_idx: int
            try:
                cycle_idx = int(args[0])
            except ValueError:
                return f"Invalid argument {args[0]} must be integer"
            self.root.cycle_active_term(cycle_idx)
            return f"Successfully cycled to term {cycle_idx}"           
        self.root.cycle_active_term()
        return "Successfully cycled"
        