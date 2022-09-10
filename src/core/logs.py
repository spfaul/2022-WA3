from datetime import datetime
import sys

class Logger:
    """
    Basic log implementation.
    Logs are required as UI utilizes the terminal screen, so any errors or debug information must be programatically stored.
    """
    def __init__(self, filepath):
        self.filepath = filepath

        # Empty our log file
        with open(self.filepath, 'w') as f:
            pass

    def log(self, msg):
        """ Append a message to logs """
        with open(self.filepath, 'a') as f:
            f.write(msg)

    def info(self, msg):
        """ Log a debug/info-related message """
        self.log(f'[INFO]: {datetime.now()} - {msg}\n')

    def warning(self, msg):
        """ Log a warning message """
        self.log(f'[WARNING]: {datetime.now()} - {msg}\n')

    def error(self, msg, exception=None):
        """ Log an error message """
        self.log(f'[ERROR]: {datetime.now()} - {msg}\n')
        # Show the exact exception raised if needed
        self.log(f'Error is as follows: {exception}\n')