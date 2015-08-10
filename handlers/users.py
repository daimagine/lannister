#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.schema import CustomerSchema
from stark.models.customer import Customer

from lannister.utils.routes import AppURL


class UserHandler(CacheJSONHandler):

	@gen.coroutine
	@auth()
	def put(self, id):
		try:
			self.db.begin()
			logger.debug('update user %s' % id)
			
			# extract body
			userParam = self.request.data['user']
			logger.debug(userParam)

			criteria = self.db.query(Customer).filter(Customer.id == id)
			customer = criteria.one()

			# update customer
			customer.name = userParam['name']
			customer.mobile_no = userParam['mobile_no']
			customer.address = userParam['address']

			# save product
			self.db.commit()

			# return response
			serializer = CustomerSchema()
			self.response['user'] = serializer.dump(customer).data
			self.response['message'] = 'Update user success'
			self.response['success'] = True

			# refresh cache
			cache_refresh(self, [self.request.path, AppURL["users"]])

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to update user')