import tweepy
from lannister.utils.logs import logger
from lannister.utils.strings import StringUtils
from lannister import settings
from lannister.interfaces.social_media.exceptions import SocmedException, SocmedPostException
from stark.models.schema import ProductSchema, CustomerSocmedAccountTokenSchema
from sociale import tasks as SocialTask


class TwitterInterface(object):
	@staticmethod
	def post(twitter_account, headline, product_page, product):
		try:
			logger.debug('TwitterInterface: post to twitter @%s' % twitter_account.social_name)
			
			params = {
				'twitter_account': CustomerSocmedAccountTokenSchema().dump(twitter_account).data,
				'headline': headline,
				'product_page' : product_page,
				'product' : ProductSchema().dump(product).data
			}
			SocialTask.post_twitter.delay(params)

		except tweepy.TweepError, errors:
			logger.exception(errors);
			error = errors.message[0]
			raise SocmedPostException(error['message'], error)


	@staticmethod
	def get_redirect_url(customer, social_media, callback_url):
		try:
			# build tweepy auth
			CONSUMER_KEY = social_media.consumer_key
			CONSUMER_SECRET = social_media.consumer_secret

			response = dict()
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			
			response['redirect_url'] = auth.get_authorization_url()
			response['request_token'] = auth.request_token

			return response

		except tweepy.TweepError, errors:
			logger.exception(errors);
			error = errors.message[0]
			raise SocmedException(error['message'], error)

	@staticmethod
	def verify(social_media, request_token, verifier):
		try:
			# build tweepy auth
			CONSUMER_KEY = social_media.consumer_key
			CONSUMER_SECRET = social_media.consumer_secret

			response = dict()
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.request_token = request_token

			# get access token
			logger.debug('TwitterInterface: request_token %s' % request_token['oauth_token'])
			logger.debug('TwitterInterface: request_token_secret %s' % request_token['oauth_token_secret'])
			logger.debug('TwitterInterface: verifier %s' % verifier)
			auth.get_access_token(verifier)

			# get account info
			api = tweepy.API(auth)
			user = api.me()
			logger.debug('TwitterInterface: twitter account %s', user)

			response['access_token'] = auth.access_token
			response['access_token_secret'] = auth.access_token_secret
			response['social_id'] = user.id
			response['social_name'] = user.screen_name
			response['image'] = user.profile_image_url

			return response

		except tweepy.TweepError, errors:
			logger.exception(errors);
			error = errors.message[0]
			raise SocmedException(error['message'], error)
