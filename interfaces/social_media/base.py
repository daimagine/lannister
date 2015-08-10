import importlib
from lannister.utils.logs import logger
from lannister.interfaces.social_media.exceptions import SocmedPostException

class SocmedInterface(object):
	@staticmethod
	def post(socmed_account, headline, product_page):
		logger.debug('SocmedInterface: post to socmed @%s' % socmed_account.social_name)
		
		if socmed_account.social_media.interface == None:
			raise SocmedPostException('Unsupported social media')
		
		# dynamically import module defined in social media's interface
		interface_name = socmed_account.social_media.interface
		interface_package = socmed_account.social_media.interface_package
		logger.debug('SocmedInterface: load interface %s %s' % (interface_package, interface_name))
		module = importlib.import_module(interface_package)
		interface = getattr(module, interface_name)
		interface.post(socmed_account, headline, product_page)