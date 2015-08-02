import tweepy
from lannister.utils.logs import logger
from lannister.utils.strings import StringUtils
from lannister import settings
from lannister.interfaces.social_media.exceptions import SocmedPostException

class TwitterInterface(object):
	@staticmethod
	def post(twitter_account, headline, product_page):
		try:
			logger.debug('TwitterInterface: post to twitter @%s' % twitter_account.social_name)
			
			# post to twitter
			social_media = twitter_account.social_media
			CONSUMER_KEY = social_media.consumer_key
			CONSUMER_SECRET = social_media.consumer_secret
			ACCESS_TOKEN = twitter_account.token
			ACCESS_TOKEN_SECRET = twitter_account.secret

			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
			api = tweepy.API(auth)

			# headline = StringUtils.ellipsis(headline, length=settings.TWEET_HEADLINE_LENGTH, suffix='')
			logger.debug('TwitterInterface: headline: %s' % headline)
			status = "%s %s" % (headline, product_page)
			api.update_status(status=status)

		except tweepy.TweepError, errors:
			error = errors.message[0]
			raise SocmedPostException(error['message'], error)