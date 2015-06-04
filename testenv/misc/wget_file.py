
class WgetFile:

    """ WgetFile is a File Data Container object """

    def __init__ (
        self,
        name,
        content="Test Contents",
        timestamp=None,
        rules=None,
        file_perm=None
	):
        self.name = name
        self.content = content
        self.timestamp = timestamp
        self.rules = rules or {}
        self.file_perm = file_perm
