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
# schema
from stark.models.customer import Customer
from stark.models.schema import CustomerSchema


class SessionHandler(JSONHandler):
    @gen.coroutine
    def post(self):
        try:
            email = self.request.data['email']
            password = self.request.data['password']
            captcha = self.request.data['captcha']

            # check captcha
            captcha_validity = verify_captcha(captcha)
            if captcha_validity != True:
                raise AuthenticationException('Invalid Captcha')
            
            # find customer by email criteria
            self.db.begin()
            criteria = self.db.query(Customer)
            logger.debug('find customer by email: %s' % email)
            criteria = criteria.filter(Customer.email == email)
            # find or fail customer
            customer = criteria.one()

            # check customer password matching
            if bcrypt.hashpw(
                password.encode('utf-8'), 
                customer.password_1.encode('utf-8')) != customer.password_1:
                    raise AuthenticationException('Invalid Credential')

            # generate client_token and client_token_valid_time
            hashed_token = bcrypt.hashpw(customer.email.encode('utf-8'), bcrypt.gensalt(14))
            encoded_token = base64.b64encode(hashed_token)
            client_token = encoded_token

            # store client_token to customer
            customer.client_token = client_token
            # 10 days expiry time
            customer.client_token_valid_time = datetime.now() + timedelta(days=10)
            self.db.commit()

            # encode customer and client_token into jwt format
            serializer = CustomerSchema()
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
            self.write_error(status_code=400, error=error.message)

        except Exception, error:
            self.db.rollback()
            logger.exception(error)
            self.write_error(status_code=500, error='Authentication Failed')


class AuthenticationException(Exception):
    ''' Raise when authentication process is failed '''