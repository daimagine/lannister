#tornado
import tornado.web
from tornado import gen
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth
import tweepy

from lannister.utils.routes import AppURL, api_version
from lannister.interfaces.social_media import constants as SocmedConstant
from lannister.interfaces.social_media.exceptions import SocmedException
from lannister.interfaces.social_media.twitter import TwitterInterface

from stark.models.social_media import SocialMedia
from stark.models.customer import Customer
from stark.models.customer_socmed_account import CustomerSocmedAccount


class AddTwitterAccountHandler(CacheJSONHandler):

	def refresh_cache(self, customerId=None):
		# refresh cache
		cache_refresh(self, [AppURL["customer_socmeds"]])


	@gen.coroutine
	@auth()
	def get(self):
		try:
			logger.debug('AddTwitterAccountHandler: request redirect url')

			self.db.begin()
			
			customer_id = self.get_argument('customer')
			callback_url = self.get_argument('callback_url')
			logger.debug('AddTwitterAccountHandler: callback_url %s' % callback_url)

			criteria = self.db.query(Customer).filter(Customer.id == customer_id)
			customer = criteria.one()

			criteria = self.db.query(SocialMedia).filter(SocialMedia.id == SocmedConstant.TWITTER)
			social_media = criteria.one()

			response = TwitterInterface.get_redirect_url(customer, social_media, callback_url)

			self.db.commit()

			self.response = response
			logger.debug(self.response)
			self.write_json()
			
		except SocmedException, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error=error.message)

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to get twitter redirect url')



	@gen.coroutine
	@auth()
	def post(self):
		try:
			logger.debug('AddTwitterAccountHandler: verify twitter account')

			self.db.begin()
			
			customer_id = self.request.data['customer_id']
			request_token = self.request.data['request_token']
			verifier = self.request.data['verifier']

			# add new twitter account to customer social media
			criteria = self.db.query(Customer).filter(Customer.id == customer_id)
			customer = criteria.one()

			criteria = self.db.query(SocialMedia).filter(SocialMedia.id == SocmedConstant.TWITTER)
			social_media = criteria.one()

			# verify twitter
			response = TwitterInterface.verify(social_media, request_token, verifier)

			socmed_account = CustomerSocmedAccount()
			socmed_account.customer = customer
			socmed_account.social_media = social_media
			socmed_account.token = response['access_token']
			socmed_account.secret = response['access_token_secret']
			socmed_account.social_id = response['social_id']
			socmed_account.social_name = response['social_name']
			socmed_account.image = response['image']
			socmed_account.type = SocmedConstant.TWITTER

			self.db.add(socmed_account)
			self.db.commit()

			self.response['twitter_account'] = response

			# refresh cache
			self.refresh_cache(customerId=customer_id)

			logger.debug(self.response)
			self.write_json()
			
		except SocmedException, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error=error.message)

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to add twitter account')
