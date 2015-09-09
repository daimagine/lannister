import importlib
from lannister.utils.logs import logger
from lannister.interfaces.social_media import constants as SOCIAL_MEDIA
from lannister.interfaces.social_media.exceptions import SocmedPostException

class SocmedInterface(object):
	@staticmethod
	def post(socmed_account, headline, product_page, product):
		try:
			if socmed_account.social_media.id == SOCIAL_MEDIA.TWITTER:
				logger.debug('SocmedInterface: post to twitter @%s' % socmed_account.social_name)
			else:
				logger.debug('SocmedInterface: post to socmed %s' % socmed_account.social_name)
			
			if socmed_account.social_media.interface == None:
				raise SocmedPostException('Unsupported social media')
			
			# dynamically import module defined in social media's interface
			interface_name = socmed_account.social_media.interface
			interface_package = socmed_account.social_media.interface_package
			logger.debug('SocmedInterface: load interface %s %s' % (interface_package, interface_name))
			module = importlib.import_module(interface_package)
			interface = getattr(module, interface_name)
			interface.post(socmed_account, headline, product_page, product)

		except Exception, error:
			logger.exception(error);
			raise SocmedPostException('Failed to post to social media')