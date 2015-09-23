from lannister.utils.logs import logger


class ParseUtil(object):
	@staticmethod
	def parseBool(str):
		return str[0].upper() == 'T'

	@staticmethod
	def parseInt(str):
		val = None
		try:
			val = int(str)
		except Exception, err:
			logger.debug('ParseUtil: failed to parse %s' % str)
		return val