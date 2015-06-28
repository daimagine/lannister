#!/usr/bin/env python
# tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
# logging
from lannister.utils.logs import logger
# settings
from lannister import settings
# application
from lannister.common.application import Application
from lannister.common.safe_httpserver import SafeHTTPServer

# cmd line options
tornado.options.define('port', type=int, default=settings.SERVER_PORT,
    help='server port number (default: %s)' % settings.SERVER_PORT)
tornado.options.define('debug', type=bool, default=settings.DEBUG_ENABLED,
    help='run in debug mode with autoreload(default: %s)' % settings.DEBUG_ENABLED)


def main():
    logger.debug('Initiate tornado server')
    tornado.options.parse_command_line()
    options = tornado.options.options
    application = Application()
    ioloop = tornado.ioloop.IOLoop.instance()

    http_server = SafeHTTPServer(application)
    http_server.listen(options.port)
    logger.info('started on port: %s', options.port)
    ioloop.start()


if __name__ == '__main__':
    main()
