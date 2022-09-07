import re

class EscCodeHandler:
    esc_regex = re.compile(r'^\x1b\[?([?\d;]*)(\w)')
    def __init__(self, logs, display):
        self.logs = logs
        self.display = display
        self.subscriber_map = {}

    def on(self, code_char, func):
        if code_char not in self.subscriber_map:
            self.subscriber_map[code_char] = [func]
            return
        self.subscriber_map[code_char].append(func)

    def dispatch(self, code_char, args):
        if code_char in self.subscriber_map:
            for f in self.subscriber_map[code_char]:
                f(self.display, *args)
        
    def handle_head(self, text):
        args, char = self._parse(text)
        if not args and not char:
            return None
        arglist = [args]
        if ";" in args:
            arglist = args.split(";")
        arglist = [arg  if arg else "0" for arg in arglist]
        self.logs.info(f"{char} - {arglist}")
        self.dispatch(char, arglist)
        return text[2+len(args)+1:] # \x1b[ = length 2, code_char = length 1

    def _parse(self, text):
        matches = self.esc_regex.match(text)
        if not matches:
            return None, None
        return matches.groups()