#tornado
import tornado.web
import json
from tornado import gen
import collections
from lannister.utils.cache import cache
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler

from stark.models.product import Product, ProductSchema
from lannister.utils.caching_query import FromCache, RelationshipCache


class ProductHandler(CacheJSONHandler):
	@gen.coroutine
	@cache(refresh_prefixes=id)
	def get(self, id=None):
		try:
			logger.debug('get products')
			logger.debug(self.request.arguments)

			criteria = self.db.query(Product)

			# filtering
			if id == None:
				# affiliate
				if 'affiliate' in self.request.arguments:
					affiliate = ParseUtil.parseBool(self.get_argument('affiliate'))
					logger.debug('affiliate criteria: %s' % affiliate)
					criteria = criteria.filter(Product.is_affiliate_ready == affiliate)

				# customer
				if 'customer' in self.request.arguments:
					customer_id = self.get_argument('customer')
					logger.debug('customer criteria: %s' % customer_id)
					criteria = criteria.filter(Product.customer_id == customer_id)

				products = criteria.all()
				serializer = ProductSchema(many= True)
				self.response['products'] = serializer.dump(products).data

			else:
				# fetch one
				criteria = self.db.query(Product).filter(Product.id == id)
				product = criteria.one()
				serializer = ProductSchema()
				self.response['product'] = serializer.dump(product).data

			self.write_json()

		except Exception as error:
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data');


	@gen.coroutine
	@cache(refresh_prefixes="")
	def post(self, id=None):
		return