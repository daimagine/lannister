from lannister.utils.logs import logger

class TwitterInterface(object):
	@staticmethod
	def post(twitter_account, headline, product_page):
		logger.debug('TwitterInterface: post to twitter @%s' % twitter_account.social_name)
		# TODO: post to twitter
		return True