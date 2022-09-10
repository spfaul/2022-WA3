import re

class EscCodeHandler:
    esc_regexs = [
        (re.compile(r'^\x1b\[(\d+)?@'), "@"),
        (re.compile(r'^\x1b\(B'), "IGNORE"),
        (re.compile(r'^\x1b\[?([?\d;]*)(\w)'), None)
    ]

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
        if char == "IGNORE":
            return text[len(args):]
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
        for pattern, char in self.esc_regexs:   
            matches = pattern.match(text)
            if matches:
                # self.logs.info(matches)
                if char == "IGNORE":
                    return matches.group(0), char
                elif char:
                    return matches.group(1), char
                return matches.groups()
        return None, None

            