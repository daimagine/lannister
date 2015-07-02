# tornado
from tornado import gen
# utils
from lannister.utils.logs import logger
from lannister.common.handler import JSONHandler
import jwt
import bcrypt
import base64
from datetime import datetime, timedelta
import time
import calendar
from lannister.utils.captcha import verify_captcha
from lannister.handlers.sessions import AuthenticationException
# schema
from stark.models.customer import Customer, CustomerAuthSchema


class AuthTokenHandler(JSONHandler):
    """Authenticate user based on token"""

    @gen.coroutine
    def post(self):
        try:
            client_token = self.request.data['client_token']
            
            # find customer by client_token and valid time criteria
            self.db.begin()
            criteria = self.db.query(Customer)
            logger.debug('find customer by client_token: %s' % client_token)
            criteria = criteria.filter(Customer.client_token == client_token)
            criteria = criteria.filter(Customer.client_token_valid_time > datetime.utcnow())
            
            # find or fail customer
            customer = criteria.one()

            # generate new client_token and client_token_valid_time
            hashed_token = bcrypt.hashpw(customer.email.encode('utf-8'), bcrypt.gensalt(14))
            encoded_token = base64.b64encode(hashed_token)
            client_token = encoded_token

            # store client_token to customer
            customer.client_token = client_token
            # 10 days expiry time
            customer.client_token_valid_time = datetime.now() + timedelta(days=10)
            self.db.commit()

            # encode customer and client_token into jwt format
            serializer = CustomerAuthSchema()
            customerSchema = serializer.dump(customer).data
            
            payload = {
                'client_token': client_token,
                'user': customerSchema
            }
            encoded = jwt.encode(payload, 'jualiosecret123')
            self.response = {
                'payload': encoded
            }

            logger.debug('response new sessions')
            self.write_json()

        except AuthenticationException, error:
            self.db.rollback()
            logger.exception(error)
            self.write_error(status_code=400, error=error.message);

        except Exception, error:
            self.db.rollback()
            logger.exception(error)
            self.write_error(status_code=500, error='authentication failed');