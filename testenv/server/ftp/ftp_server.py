from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
import threading
import socket

class StoppableFTPServer(FTPServer):
	def server_conf(self, filelist, conf_dict):
		self.server_configs = conf_dict
		self.fileSys = filelist

class _FTPHandler(FTPHandler):
	pass

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

