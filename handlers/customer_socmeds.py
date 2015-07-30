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

from lannister.utils.routes import AppURL


class CustomerSocmedHandler(CacheJSONHandler):
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
			self.write_error(status_code=500, error='Failed to fetch data');
