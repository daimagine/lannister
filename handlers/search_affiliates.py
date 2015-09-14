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
				criteria = criteria.filter(Product.name.ilike(name))
			
			if 'seller' in self.request.arguments:
				name = "%" + self.get_argument('seller') + "%"
				logger.debug('seller criteria: %s' % name)
				criteria = criteria.join(Customer)
				criteria = criteria.filter(Customer.name.ilike(name))

			if 'price_min' in self.request.arguments:
				price_min = ParseUtil.parseInt(self.get_argument('price_min'))
				logger.debug('price min criteria: %s' % price_min)
				if price_min != None and price_min > 0:
					criteria = criteria.filter(Product.price >= price_min)

			if 'price_max' in self.request.arguments:
				price_max = ParseUtil.parseInt(self.get_argument('price_max'))
				logger.debug('price min criteria: %s' % price_max)
				if price_max != None and price_max > 0:
					criteria = criteria.filter(Product.price <= price_max)
			
			if 'fee_min' in self.request.arguments:
				fee_min = ParseUtil.parseInt(self.get_argument('fee_min'))
				logger.debug('fee_min criteria: %s' % fee_min)
				if fee_min != None and fee_min > 0:
					criteria = criteria.filter(Product.affiliate_fee >= fee_min)
			
			if 'fee_max' in self.request.arguments:
				fee_max = ParseUtil.parseInt(self.get_argument('fee_max'))
				logger.debug('fee_max criteria: %s' % fee_max)
				if fee_max != None and fee_max > 0:
					criteria = criteria.filter(Product.affiliate_fee <= fee_max)

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

			# sort
			if 'sort' in self.request.arguments:
				sort = self.get_argument('sort')
				logger.debug('sort criteria: %s' % sort)
				# if desc use self.desc

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