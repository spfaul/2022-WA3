import shlex
import sys

class DefaultCommandSet:
    def __init__(self):
        self.command_map = {}

    def command_not_found(self, args):
        return f"Unknown command {args[0]}, try: \"help\""

    def add_command(self, func):
        self.command_map[func.__name__] = func

    def process(self, text):
        tokens = shlex.split(text)
        if not len(tokens):
            return
        if tokens[0] in self.command_map:
            return self.command_map[tokens[0]](tokens[1:])
        else:
            return self.command_not_found(tokens)
            

class BasicCommandSet(DefaultCommandSet):
    def __init__(self, master_win):
        super().__init__()
        self.root = master_win
        self.add_command(self.quit)
        self.add_command(self.hsplit)
        self.add_command(self.vsplit)
        self.add_command(self.help)
        self.add_command(self.cycle)
            
    def quit(self, args):
        self.root.running = False

    def hsplit(self, args):
        self.root.create_term_right()
        return f"Term split successfully. There are {len(self.root.term_wins)} active sessions."

    def vsplit(self, args):
        self.root.create_term_down()
        return f"Term split successfully. There are {len(self.root.term_wins)} active sessions."

    def help(self, args):
        all_commands = ", ".join(list(self.command_map.keys()))
        return f"Available Commands: {all_commands}"

    def cycle(self, args):
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
        