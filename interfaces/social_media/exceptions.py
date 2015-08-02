
class SocmedPostException(Exception):
    ''' Raise when socmed posting is failed '''
    def __init__(self, message, errors):
    	super(Exception, self).__init__(message)
    	self.errors = errors