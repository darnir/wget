from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from exc.server_error import AuthError
import threading
import sys
import os


class StoppableFTPServer(FTPServer):
    def server_conf(self, filelist, conf_dict):
        self.server_configs = conf_dict
        self.fileSys = filelist


class _FTPHandler(FTPHandler):
    def pre_process_command(self, line, cmd, arg):
        """
        Overriding method to remove filesystem dependencies
        """
        if self.proto_cmds[cmd]['perm']:
            if cmd == 'CWD':
                arg = "/"
            elif cmd == 'LIST':
                arg = "/"
            """
            else:
                arg = "/"
            """

        self.process_command(cmd, arg)

    def ftp_USER(self, line):
        """ Overriding ftp_USER method.
        Set the username for the current session.
        """
        if not self.authenticated:
            self.respond('331 Username OK, Waiting for password')

        self.username = line

    def ftp_PASS(self, line):
        """
        Method to handle PASS command. This method is independent of
        authorizers.
        """
        if self.authenticated:
            self.respond("503 User is already authenticated")
            return
        if not self.username:
            self.respond("503 Login with USER first")
            return
        try:
            msg_login = "Login successful"
            self.respond('230 %s' % msg_login)
            self.log("USER '%s' logged in." % self.username)
            self.authenticated = True
            self.password = line
        except AuthError as se:
            self.respond('Login failed')
            raise se

    def ftp_SIZE(self, path):
        """Method to return size of file to the client"""
        if self._current_type == 'a':
            why = "SIZE not allowed in ASCII mode"
            self.respond("550 %s." % why)
            return

        req_file = self.server.fileSys[path]
        size = len(req_file)
        self.respond('213 %s' % size)

    def ftp_RETR(self, file):
        """Method to retrive the file."""
        rest_pos = self._restart_position
        self._restart_position = 0

        """ We have requested file name. So retriving the contents of file
        name"""

        file_contents = self.server.fileSys[file]

        """Writing all the contents to the file."""

        f = open("File1", 'w')
        f.write(file_contents)

        fd = open("File1", 'r')

        producer = FileProducer(fd, self._current_type)
        self.push_dtp_data(producer, isproducer=True, file=fd, cmd="RETR")
        return file


class _FileReadWriteError(OSError):
    """Exception raised when reading or writing a file during a transfer."""


class FileProducer(object):
    """Producer wrapper for file[-like] objects."""

    buffer_size = 65536

    def __init__(self, file, type):
        """Initialize the producer with a data_wrapper appropriate to TYPE.

         - (file) file: the file[-like] object.
         - (str) type: the current TYPE, 'a' (ASCII) or 'i' (binary).
        """
        self.file = file
        self.type = type
        if type == 'a' and os.linesep != '\r\n':
            self._data_wrapper = lambda x: x.replace(b(os.linesep), b('\r\n'))
        else:
            self._data_wrapper = None

    def more(self):
        """Attempt a chunk of data of size self.buffer_size."""
        try:
            data = self.file.read(self.buffer_size)
        except OSError:
            err = sys.exc_info()[1]
            raise _FileReadWriteError(err)
        else:
            if self._data_wrapper is not None:
                data = self._data_wrapper(data)
            return data


class FTPd(threading.Thread):
    server_class = StoppableFTPServer
    handler = _FTPHandler
    handler.use_sendfile = False

    def __init__(self, addr=None):

        threading.Thread.__init__(self)
        if addr is None:
            addr = ('localhost', 0)
        self.server_inst = self.server_class(addr, self.handler)
        self.server_address = self.server_inst.socket.getsockname()[:2]

    def run(self):
        self.server_inst.serve_forever()

    def server_conf(self, file_list, server_rules):
        self.server_inst.server_conf(file_list, server_rules)
