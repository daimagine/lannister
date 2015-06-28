import urllib
import json
from urllib2 import Request, urlopen, URLError, HTTPError
from lannister.utils.logs import logger


def verify_captcha(captcha):
    try:
        captchaURL = "https://www.google.com/recaptcha/api/siteverify"
        secret = "6Lc4zggTAAAAAIAO8HwV79QEIhZGaU5YjqtWKihu"

        data = urllib.urlencode({
        	'secret': secret,
        	'response': captcha
        })

        request = Request(captchaURL, data)
        response = urlopen(request)
        api_response = json.loads(response.read())

        logger.debug('captcha response')
        logger.debug(api_response)
        return api_response['success']

    except HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    except URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    
    return false