"""
Main entry point of project
"""
import os
import curses
from core.logs import Logger
from ui.master_window import MasterWindow


class Application:
    """ The main application class where all the important components will live as members """
    def __init__(self, logs):
        self.logs = logs
        logs.info("Application initialised")        

    def run(self, stdscr):
        """ Main application loop """
        curses.use_default_colors()
        stdscr.nodelay(True)
        self.win = MasterWindow(logs, stdscr)
        self.win.run()
        
if __name__ == '__main__':
    logs = Logger(os.path.dirname(__file__) + "/../logs/runtime.log")
    app = Application(logs)
    curses.wrapper(app.run)