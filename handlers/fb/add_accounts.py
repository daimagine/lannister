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
from lannister.interfaces.social_media.fb import FacebookInterface

from stark.models.social_media import SocialMedia
from stark.models.customer import Customer
from stark.models.customer_socmed_account import CustomerSocmedAccount


class AddFbAccountHandler(CacheJSONHandler):

	def refresh_cache(self, customerId=None):
		# refresh cache
		cache_refresh(self, [AppURL["customer_socmeds"]])


	@gen.coroutine
	@auth()
	def get(self):
		try:
			logger.debug('AddFbAccountHandler: request redirect url')

			self.db.begin()
			
			customer_id = self.get_argument('customer')
			callback_url = self.get_argument('callback_url')
			logger.debug('AddFbAccountHandler: callback_url %s' % callback_url)

			criteria = self.db.query(Customer).filter(Customer.id == customer_id)
			customer = criteria.one()

			criteria = self.db.query(SocialMedia).filter(SocialMedia.id == SocmedConstant.FACEBOOK)
			social_media = criteria.one()

			response = FacebookInterface.get_redirect_url(customer, social_media, callback_url)

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
			self.write_error(status_code=500, error='Failed to get facebook redirect url')


	@gen.coroutine
	@auth()
	def post(self):
		try:
			logger.debug('AddFbAccountHandler: verify fb account')

			self.db.begin()
			
			customer_id = self.request.data['customer_id']
			verifier = self.request.data['verifier']
			callback_url = self.request.data['callback_url']

			# add new facebook account to customer social media
			criteria = self.db.query(Customer).filter(Customer.id == customer_id)
			customer = criteria.one()

			criteria = self.db.query(SocialMedia).filter(SocialMedia.id == SocmedConstant.FACEBOOK)
			social_media = criteria.one()

			# verify facebook
			response = FacebookInterface.verify(social_media, verifier, callback_url)

			# check for duplicate
			criteria = self.db.query(CustomerSocmedAccount)
			criteria = criteria.filter(CustomerSocmedAccount.customer == customer)
			criteria = criteria.filter(CustomerSocmedAccount.social_media == social_media)
			criteria = criteria.filter(CustomerSocmedAccount.social_id == response['social_id'])
			count = criteria.count()

			if (count < 1):
				socmed_account = CustomerSocmedAccount()
				socmed_account.customer = customer
				socmed_account.social_media = social_media
				socmed_account.token = response['access_token']
				socmed_account.social_id = response['social_id']
				socmed_account.social_name = response['social_name']
				socmed_account.image = response['image']
				socmed_account.type = SocmedConstant.FACEBOOK

				# add only if not exist
				logger.debug('AddFbAccountHandler: add customer_socmed_account')
				self.db.add(socmed_account)

			else:
				logger.debug('AddFbAccountHandler: customer_socmed_account already registered')

			# commit
			self.db.commit()

			self.response['fb_account'] = response

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
			self.write_error(status_code=500, error='Failed to add facebook account')
