# General description of project
> E.g. Building an inventory tracking system for my CCA

A terminal multiplexer for UNIX systems, (in OOP, of course). Allows a user to interact with multiple terminal sessions with ease through a single terminal window. Users can utilise keybindings to conveniently jump between terminal sessions, allowing for better productivity.

> Why UNIX?

From my googling i noticed there isn't any official pty/tty support for DOS from the python folks, and while [external libraries](https://pypi.org/project/pywinpty/) do exist, i want to build this from scratch as much as possible. However I still plan on using the `curses` module (ported version of GNU ncurses) because I feel that writing my own TUI implementation would not only be gruesomely painful, but also take precious time away from the main focus of the project.

# Goals of project
> E.g. Streamline tracking and cataloguing of inventory to facilitate member loans, repairs & Semester stock-taking needs

Streamline working in the terminal by making managing multiple terminal sessions more feasable and productive, just to make the lives of the DevOps folks and everyday programmers a little less painful. No one likes having to repeatedly Alt-Tab between 2 terminal windows (or just windows in general). Literally no one.

# Listing of features
> List all the features in the fully functional app - you may choose to work on a subset of this listing to produce a MVP (minimum viable product) given constraint of time

# External Scanning
> Are there similar apps / codebase that you found online that is similar to your project?  Provide link(s) to these projects and outline how will your project be different?

[tmux](https://github.com/tmux/tmux) - The main inspiration for this project. Built with C in 2007, it lacks OOP structure simply due to the limitations of C. My project plans to extend certain features of tmux (refer above).

[pytmux](https://github.com/arthaud/pytmux) - Tmux clone in python. It's a simple POC, only 1 main file (1000 lines!) which lacks coherent structure. Although using OOP, it doesn't include 99% of the core features of tmux. Just one emulated terminal window and that's it.

[pymux](https://github.com/prompt-toolkit/pymux) - Another tmux clone in python. Blazingly slow (its python so whatever), relies on heavy imports from external libraries. Also discontinued 2 years ago, so its basically legacy code at this point.


# Listing of Key Use Cases
> Yearly, CCA senior will do stock-take and will need to generate a report on the existing stock.
> Start of school break, members will loan equipment and will need to return when school break ends.

Using the terminal is a basic skill for any developer entering the workforce. A sizeable (although minority) portion of developers also use terminal-based editors (e.g. vim, emacs).

- Switiching between terminal windows with ease boosts productivity significantly.

- Allows you to monitor a background process (e.g. system logs) while working on other stuff


# Skills that my project requires me to pick up
> List out the skills that you are not familiar with that is necessary due to the project scope.

- curses
- ANSI escape codes
- Unicode
- Terminal interaction (signals, etc.)
- Logging
- Configurations
- ttys and ptys

# [Development Log](/devlog.md)
> You will be updating this section regularly
> - Week 5
> - Week 6
> - Week 7
> - Week 8
> - Week 9
> - Week 10
