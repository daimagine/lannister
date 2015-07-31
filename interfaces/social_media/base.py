import importlib
from lannister.utils.logs import logger
from lannister.interfaces.social_media.exceptions import SocmedPostException

class SocmedInterface(object):
	@staticmethod
	def post(socmed_account, headline, product_page):
		logger.debug('SocmedInterface: post to socmed @%s' % socmed_account.social_name)
		
		if socmed_account.social_media.plugin == None:
			raise SocmedPostException('Unsupported social media')
		
		# dynamically import module defined in social media's plugin
		plugin = socmed_account.social_media.plugin
		plugin_package = socmed_account.social_media.plugin_package
		logger.debug('SocmedInterface: load interface %s %s' % (plugin_package, plugin))
		module = importlib.import_module(plugin_package)
		interface = getattr(module, plugin)
		response = interface.post(socmed_account, headline, product_page)

		return response