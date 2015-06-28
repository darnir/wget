#!/usr/bin/env python3
from sys import exit
from test.ftp_test import FTPTest
from test.base_test import FTP
from misc.wget_file import WgetFile

"""
    This test ensures that Wget can download files from FTP Server
"""
TEST_NAME = "FTP Downloads"
########## File Definitions ######################################
File1 = "Beyond the fog lies clarity"

A_File = WgetFile("File1", File1)

WGET_OPTIONS = " -S "
WGET_URLS = [["File1"]]

Files = [[A_File]]

Servers = [FTP]

ExpectedReturnCode = 0
ExpectedDownloadedFiles = [A_File]

######### Pre and Post Test Hooks ################################
pre_test = {
    "ServerFiles"     : Files
}
test_options = {
    "WgetCommands"    : WGET_OPTIONS,
    "Urls"            : WGET_URLS
}
post_test = {
    "ExpectedFiles"   : ExpectedDownloadedFiles,
    "ExpectedRetCode" : ExpectedReturnCode
}

err = FTPTest(
              name=TEST_NAME,
              pre_hook=pre_test,
              test_params=test_options,
              post_hook=post_test,
              protocols=Servers
).begin()

exit(err)
