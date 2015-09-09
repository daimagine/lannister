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
from lannister.utils.caching_query import FromCache, RelationshipCache

from lannister.utils.routes import AppURL

class SearchAffiliatesHandler(CacheJSONHandler):
	@gen.coroutine
	@auth()
	@cache()
	def get(self):
		try:
			logger.debug('search affiliate products')
			logger.debug(self.request.arguments)

			self.db.begin()
			criteria = self.db.query(Product).distinct(Product.id).group_by(Product.id)

			# name filter
			if 'name' in self.request.arguments:
				name = "%" + self.get_argument('name') + "%"
				logger.debug('name criteria: %s' % name)
				criteria = criteria.filter(Product.name.like(name))

			# affiliate ready filter
			affiliate = True
			logger.debug('affiliate criteria: %s' % affiliate)
			criteria = criteria.filter(Product.is_affiliate_ready == affiliate)

			# find product which is not customer's product
			customer_id = self.get_argument('customer')
			logger.debug('customer criteria: %s' % customer_id)
			criteria = criteria.filter(Product.customer_id != customer_id)

			# find product which is have not affiliated by the customer
			# logger.debug('affiliate exist criteria: %s' % customer_id)
			# affiliate_subs = self.db.query(Product.id).join(Affiliate)
			# affiliate_subs = affiliate_subs.filter(Affiliate.customer_id == customer_id)
			# affiliate_subs = affiliate_subs.distinct(Product.id)
			# criteria = criteria.filter(self.sql.not_(Product.id.in_(affiliate_subs.subquery())))

			products = criteria.all()
			serializer = ProductSchema(many= True)
			self.response['products'] = serializer.dump(products).data

			self.db.commit()
			logger.debug('found %i products' % len(products))
			self.write_json()

		except Exception as error:
			self.db.rollback()
			logger.exception(error.message)
			self.write_error(status_code=500, error='Failed to fetch data');