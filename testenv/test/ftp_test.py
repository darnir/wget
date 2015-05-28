#!/usr/bin/env python3
from misc.colour_terminal import print_green
from server.ftp.ftp_server.py import FTPd
from test.base_test import BaseTest, FTP

class FTPTest(BaseTest):
	""" Class for FTP Tests """
	""" Class that defines methods to start and stop FTP server """ 
	def __init__(self,
			name = "Unnamed Test",
			pre_hook = None,
			test_params = None,
			post_hook = None,
			protocols = (FTP)):
		super(FTPTest, self).__init__(name,
						pre_hook,
						test_params,
						post_hook,
						protocols)
		with self:
			self.server_setup()
			self.do_test()
			print_green('Test Passed.')
			
	def instantiate_server_by(self, protocol):
		server = {FTP: FTPd}[protocol]()
		server.start()
		return server
		
	def stop_server(self):
		for server in self.servers:
			server.server_inst.shutdown()
#vim: set ts=4 sts=4 sw=4 tw=80 
