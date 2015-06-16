
class ParseUtil(object):
	@staticmethod
	def parseBool(str):
		return str[0].upper() == 'T'