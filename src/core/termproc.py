import signal
import termios
import struct
import fcntl
import pty
import subprocess
import os
import sys

class TerminalProcess:
    def __init__(self):
        master, slave = pty.openpty() # Open a psuedoterminal pair with  master controlling slave's io
        self.proc = subprocess.Popen(args=[os.environ.get('SHELL', '/bin/sh')],
                                    env=os.environ,
                                    stdin=slave,
                                    stdout=slave,
                                    stderr=slave,
                                    close_fds=True,
                                    preexec_fn=self.preinit_fn)

        # Create psuedo-iobuffers by opening fd copies of master
        self.stdin = os.fdopen(os.dup(master), 'r+b', 0)
        self.stderr = os.fdopen(os.dup(master), 'r+b', 0)
        # Make stdout non-blocking
        stdoutfd = os.dup(master) 
        fl = fcntl.fcntl(stdoutfd, fcntl.F_GETFL)
        fcntl.fcntl(stdoutfd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        self.stdout = os.fdopen(stdoutfd, 'r+b', 0)
        
        # Don't need master and slave open anymore
        os.close(master)
        os.close(slave)

    def preinit_fn(self):
        '''
        Taken from https://github.com/Gallopsled/pwntools/blob/493a3e3d925a87dbbfc90423f0d02cf72724fade/pwnlib/tubes/process.py#L774
        
        Routine executed in the child process before invoking execve().
        This makes the pseudo-terminal the controlling tty. This should be
        more portable than the pty.fork() function.
        '''
        child_name = os.ttyname(0)

        # Disconnect from controlling tty. Harmless if not already connected.
        try:
            fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
            if fd >= 0:
                os.close(fd)
        except OSError:
            pass  # Already disconnected

        os.setsid()

        # Verify we are disconnected from controlling tty
        # by attempting to open it again.
        try:
            fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
            if fd >= 0:
                os.close(fd)
                raise Exception('Failed to disconnect from controlling tty. '
                                'It is still possible to open /dev/tty.')
        except OSError:
            pass  # Good! We are disconnected from a controlling tty.

        # Verify we can open the child pty.
        fd = os.open(child_name, os.O_RDWR)
        if fd < 0:
            raise Exception('Could not open child pty, %s' % child_name)
        else:
            os.close(fd)

        # Verify we now have a controlling tty.
        fd = os.open('/dev/tty', os.O_WRONLY)
        if fd < 0:
            raise Exception('Could not open controlling tty, /dev/tty')
        else:
            os.close(fd)

    def read(self, fd, amnt_bytes):
        try:
            chunk = fd.read(amnt_bytes)
            if chunk is None:
                return None
            return chunk.decode('utf8', 'replace')
        except OSError: # Nothing to read
            return ''

    def send(self, line):
        self.stdin.write(line)

    def resize(self, lines, cols):
        fcntl.ioctl(self.stdout, termios.TIOCSWINSZ, struct.pack("hhhh", lines, cols, 0, 0))
        self.proc.send_signal(signal.SIGWINCH)
        