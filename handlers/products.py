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

class ProductHandler(CacheJSONHandler):
	@gen.coroutine
	def get(self, id=None):
		try:
			criteria = self.db.query(Product)
			if id == None:
				# filtering
				if 'affiliate' in self.request.arguments:
					affiliate = ParseUtil.parseBool(self.get_argument('affiliate'))
					logger.debug('affiliate criteria: %s' % affiliate)
					criteria = criteria.filter(Product.is_affiliate_ready == affiliate)

				products = criteria.all()
				serializer = ProductSchema(many= True)
				self.response = serializer.dump(products).data

			else:
				criteria = self.db.query(Product).filter(Product.id == id)
				product = criteria.one()
				serializer = ProductSchema()
				self.response = serializer.dump(product).data

			self.write_json()

		except Exception as error:
			logger.exception(error.message)
			message = 'Failed to fetch data'
			self.send_error(500, message=message)