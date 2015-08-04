
class SocmedException(Exception):
    ''' Raise when socmed action is failed '''
    def __init__(self, message, errors):
    	super(Exception, self).__init__(message)
    	self.errors = errors


class SocmedPostException(SocmedException):
    ''' Raise when socmed posting is failed '''