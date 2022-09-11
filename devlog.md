# Development Log
> A successful final project is built slowly over many weeks not thrown together at the last minute. To incentivize good project pacing and to let your project mentor stay informed about the status of your work, each week you should add an entry to your log.md file in the development directory.

> Each entry should describe:

> - What goals you had set for the week and whether they were accomplished or not
> - What problems you encountered (if any) that prevented you from meeting your goals
> - What you plan to accomplish or attempt next week

> The development log will be graded for completion, detail, and honesty – not progress. It is much better to truthfully evaluate the work you completed in a week then lie to make the project sound further along then it really is. It is totally acceptable to have an entry that says you tried nothing and accomplished nothing. However if every week starts to say that, both yourself and your project mentor will be able to identify the issue before it becomes impossible to fix.

[Example of Good/Bad Changelist descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html)

## Week 5 (26 Jul - 1 Aug)
- Goals
    - [x] Get a basic hello-world TUI working
    - [x] Create basic logger
    - [x] Create basic keyboard dispatcher
    - [ ] Create pty process class
- Problems
    - DOS Compatibility (only targeting UNIX now, lol)
- Next week
    - [ ] Create pty process class
    - [ ] Forward output of pty process to TerminalWindow TUI 
    
## Week 6 (2 Aug - 8 Aug)
- Goals
    - [x] Create pty process class    
    - [x] Forward output of pty process to TerminalWindow TUI (sloppy wip)
- Problems
    - Exams
- Next week
    - [ ] ANSI escape code parsing
    - [ ] Clean output of termproc before forwarding to UI
## Week 7 (9 Aug - 15 Aug)
- Goals
    - [x] ANSI escape code parsing (no implementation on encounter, just dispatch and identification)    
    - [x] Clean output of termproc before forwarding to UI
- Problems
    - NA
- Next week
    - [ ] ANSI escape code encounter implementation 
## Week 8 (16 Aug - 22 Aug)
- Goals
    - Ended up doing nothing because of too many commitments
## Week 9 (23 Aug - 29 Aug)
- Goals
    - [x] Small bugfixes within escape code handling
- Problems
    - Exams and lack of time
## Week 10 (30 Aug - 5 Sep)
- Goals
    - [x] Backspace and arrow key cursor manipulation
    - [ ] Splitting windows
- Problems
    - NA
## Sep Holiday (5 Sep - 10 Sep) **Submission date is 10 Sep**
- Goals
    - [x] Docstrings, type hints and comments
    - [x] Implement splitting and cycling of windows
    - [x] Command line UI
    - [x] Cleanup code
- Problems
    - User keystrokes are detected unreliably
        - Migrated from curses getch() to a homemade getch() reading from stdin