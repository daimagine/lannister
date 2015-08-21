#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.schema import CustomerSocmedAccountSchema
from stark.models.customer import Customer
from stark.models.customer_socmed_account import CustomerSocmedAccount
from lannister.utils.caching_query import FromCache, RelationshipCache

from lannister.utils.routes import AppURL, api_version


class CustomerSocmedHandler(CacheJSONHandler):

	def refresh_cache(self, socmedAccountId=None):
		# refresh cache
		url = "%s/customer_socmeds/%s" % (api_version, socmedAccountId)
		cache_refresh(self, [AppURL["customer_socmeds"], url])


	@gen.coroutine
	@auth()
	@cache()
	def get(self, id=None):
		try:
			logger.debug('get customer socmed')
			logger.debug(self.request.arguments)

			self.db.begin()
			criteria = self.db.query(CustomerSocmedAccount)

			# filtering
			if id == None:
				# customer
				if 'customer' in self.request.arguments:
					customer_id = self.get_argument('customer')
					logger.debug('customer criteria: %s' % customer_id)
					criteria = criteria.filter(CustomerSocmedAccount.customer_id == customer_id)

				socmedAccounts = criteria.all()
				serializer = CustomerSocmedAccountSchema(many= True)
				self.response['social_media_accounts'] = serializer.dump(socmedAccounts).data

			else:
				# fetch one
				criteria = self.db.query(CustomerSocmedAccount).filter(CustomerSocmedAccount.id == id)
				socmedAccount = criteria.one()
				serializer = CustomerSocmedAccountSchema()
				self.response['social_media_account'] = serializer.dump(socmedAccount).data

			self.db.commit()
			logger.debug(self.response)
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data')


	@gen.coroutine
	@auth()
	def delete(self, id):
		try:
			self.db.begin()
			logger.debug('remove customer socmed accounts %s' % id)
			
			# get customer socmed account
			criteria = self.db.query(CustomerSocmedAccount)
			criteria = criteria.filter(CustomerSocmedAccount.id == id)
			socmedAccount = criteria.one()

			# remove customer socmed account
			self.db.delete(socmedAccount)

			# commit
			self.db.commit()

			# return response
			self.response['message'] = 'Remove customer socmed account success'
			self.response['success'] = True

			# refresh cache
			self.refresh_cache(socmedAccountId=id)

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to remove customer socmed account')
