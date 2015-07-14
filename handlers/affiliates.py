#tornado
import tornado.web
from tornado import gen
import collections
from lannister.utils.cache import cache, cache_refresh
from lannister.utils.logs import logger
from lannister.utils.parse import ParseUtil
from lannister.common.handler import JSONHandler, CacheJSONHandler, auth

from stark.models.schema import ProductSchema
from stark.models.product import Product
from stark.models.affiliate import Affiliate
from stark.models.customer import Customer

import re
from lannister.utils.routes import AppURL, api_version


class AffiliateHandler(JSONHandler):
	@gen.coroutine
	def post(self, id):
		try:
			self.db.begin()
			logger.debug('join products affiliate %s' % id)
			
			# extract body
			customer_id = self.request.data['customer_id']
			logger.debug('customer %s' % customer_id)

			# get customer
			criteria = self.db.query(Customer).filter(Customer.id == customer_id)
			customer = criteria.one()

			criteria = self.db.query(Product).filter(Product.id == id)
			product = criteria.one()

			# create new affiliate
			affiliate = Affiliate(product=product, customer=customer)
			product.affiliates.append(affiliate)

			# save product
			self.db.commit()

			# return response
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data
			self.response['message'] = 'Join affiliate success'
			self.response['success'] = True

			# refresh cache
			product_url = "%s/products/%s" % (api_version, id)
			cache_refresh(self, [AppURL["products"], product_url])

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to join affiliate')


	@gen.coroutine
	def delete(self, id):
		try:
			self.db.begin()
			logger.debug('remove products affiliate %s' % id)
			
			# extract body
			customer_id = self.request.data['customer_id']
			logger.debug('customer %s' % customer_id)

			# get affiliate
			criteria = self.db.query(Affiliate)
			criteria = criteria.filter(Affiliate.product_id == id)
			criteria = criteria.filter(Affiliate.customer_id == customer_id)
			affiliate = criteria.one()

			# remove affiliate
			self.db.delete(affiliate)

			# commit
			self.db.commit()

			# get updated product
			self.db.begin()

			criteria = self.db.query(Product).filter(Product.id == id)
			product = criteria.one()

			self.db.commit()

			# return response
			serializer = ProductSchema()
			self.response['product'] = serializer.dump(product).data
			self.response['message'] = 'Remove affiliate success'
			self.response['success'] = True

			# refresh cache
			product_url = "%s/products/%s" % (api_version, id)
			cache_refresh(self, [AppURL["products"], product_url])

			logger.debug(self.response)
			self.write_json()

		except Exception, error:
			self.db.rollback()
			logger.exception(error)
			self.write_error(status_code=500, error='Failed to remove affiliate')