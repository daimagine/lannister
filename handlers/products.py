#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.product import Product, ProductSchema
from lannister.utils.caching_query import FromCache, RelationshipCache

import re
from lannister.utils.routes import AppURL

class ProductHandler(CacheJSONHandler):
	@gen.coroutine
	@auth()
	@cache()
	def get(self, id=None):
		try:
			logger.debug('get products')
			logger.debug(self.request.arguments)

			self.db.begin()
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

			self.db.commit()
			logger.debug(self.response)
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data');

	@gen.coroutine
	def post(self, id):
		try:
			self.db.begin()
			logger.debug('post products %s' % id)
			
			# extract body
			productParam = self.request.data['product']
			logger.debug(productParam)

			criteria = self.db.query(Product).filter(Product.id == id)
			product = criteria.one()

			# update affiliate
			product.is_affiliate_ready = productParam['is_affiliate_ready']
			product.affiliate_fee = productParam['affiliate_fee']

			# save product
			self.db.commit()

			# return response
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data
			self.response['message'] = 'Update product success'
			self.response['success'] = True

			# refresh cache
			cache_refresh(self, [self.request.path, AppURL["products"]])

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to save product')