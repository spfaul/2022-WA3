"""
Main entry point of project
"""
import logs
import os

class Application:
    """ The main application class where all the important components will live as members """
    def __init__(self, logs):
        self.logs = logs
        logs.info("Application initialised")
        
if __name__ == '__main__':
    logs = logs.Logger(os.path.dirname(__file__) + "/../logs/runtime.log")
    app = Application(logs)
    