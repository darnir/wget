from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
import threading
import socket

class StoppableFTPServer(FTPServer):
    def server_conf(self, filelist, conf_dict):
        self.server_configs = conf_dict
        self.fileSys = filelist

class _FTPHandler(FTPHandler):
    def pre_process_command(self, line, cmd, arg):
        """
        Overriding method to remove filesystem dependencies
        """
        if cmd == "SITE" and arg:
            cmd = "SITE %s" % arg.split(' ')[0].upper()
            arg = line[len(cmd) + 1:]

        if cmd != 'PASS':
            self.logline("<- %s" % line)
        else:
            self.logline("<- %s %s" %(line.split(' ')[0], '*' * 6)
        
        if cmd not in self.proto_cmds:
            if cmd[-4:] in ('ABOR' , 'STAT' , 'QUIT'):
                cmd = cmd[-4:]
            else:
                msg = 'Command %s not understood.' % cmd
                self.respond('500 ', msg)
                if cmd:
                    self.log_cmd(cmd, arg, 500, msg)
                return

        if not arg and self.proto_cmds[cmd]['arg'] == True:
            msg = 'Syntax error: command needs an argument.'
            self.respond("501 " + msg)
            self.log_cmd(cmd, "", 501, msg)
            return
        if arg and self.proto_cmds[cmd]['arg'] == False:
            msg = "Syntax error: command does not accept arguments."
            self.respond("501 " + msg)
            self.log_cmd(cmd, arg, 501,msg)
            return

        if not self.authenticated:
            if self.proto_cmds[cmd]['auth'] or (cmd == 'STAT' and arg):
                msg = "Log in with USER and PASS first."
                self.respond("530 " + msg)
                self.log_cmd(cmd, arg, 530, msg)
            else:
                self.process_command(cmd, arg)
                return
        
            """
            Filesystem and commands related contents goes here.
            """
        
        else:
            if self.proto_cmds[cmd]['perm'] :
                if cmd == 'CWD':
                    arg = "/"
                elif cmd == 'LIST':
                    arg = "/"
                else:
                    arg = "/"

        self.process_command(self, cmd, **kwargs)


class FTPd(threading.Thread):
    server_class = StoppableFTPServer
    handler = _FTPHandler
	
    def __init__(self, addr=None):
        threading.Thread.__init__(self)
        if addr is None:
            addr = ('localhost',0)
            self.server_inst = self.server_class(addr,self.handler)
            self.server_address = self.server_inst.socket.getsockname()[:2]
		
    def run(self):
        self.server_inst.serve_forever()
	
    def server_conf(self, file_list, server_rules):
        self.server_inst.server_conf(file_list, server_rules)

