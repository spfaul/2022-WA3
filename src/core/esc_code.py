import re
from typing import Callable, List

class EscCodeHandler:
    """
    ANSI Escape code backend parser and dispatcher
    """
    esc_regexs = [
        (re.compile(r'^\x1b\[(\d+)?@'), "@"),
        (re.compile(r'^\x1b\(B'), "IGNORE"),
        (re.compile(r'^\x1b\[?([?\d;]*)(\w)'), None)
    ]
    
    def __init__(self, logs, display) -> None:
        self.logs = logs
        self.display = display
        self.subscriber_map: dict[str, Callable[str]] = {}

    def on(self, code_char: str, func: Callable[[str], None]) -> None:
        """ Attach listeners according to type of escape code """
        if code_char not in self.subscriber_map:
            self.subscriber_map[code_char] = [func]
            return
        self.subscriber_map[code_char].append(func)

    def dispatch(self, code_char: str, args: List[str]) -> None:
        """ Send escape code information to respective listeners """
        if code_char in self.subscriber_map:
            for f in self.subscriber_map[code_char]:
                f(self.display, *args)
        
    def handle_head(self, text: str) -> str:
        """
        Chop escape code off the start of string, if present
        """
        args, char = self._parse(text)
        if char == "IGNORE": # Remove esc code from text and carry on
            return text[len(args):]
        if not args and not char: # No escape code found
            return None
            
        # Extract multiple args
        arglist = [args]
        if ";" in args:
            arglist = args.split(";")
        arglist = [arg  if arg else "0" for arg in arglist] # Fill empty args as "0" to be passed as param to listeners
        self.logs.info(f"Escape Code: {char} - Args: {arglist}")
        self.dispatch(char, arglist)
        return text[2+len(args)+1:] # \x1b[ = length 2, code_char = length 1

    def _parse(self, text: str):
        """
        Identify escape codes and extract their args
        """
        for pattern, char in self.esc_regexs:   
            matches = pattern.match(text)
            if matches:
                if char == "IGNORE": # Ignore this escape code and carry on
                    return matches.group(0), char
                elif char: # Return hardcoded character for pattern
                    return matches.group(1), char
                return matches.groups() # Character and args already captured in pattern
        return None, None # No escape code found