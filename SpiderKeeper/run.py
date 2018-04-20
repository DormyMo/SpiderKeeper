import logging
import os
from optparse import OptionParser

from SpiderKeeper.app import app, initialize


def main():
    opts, args = parse_opts(app.config)
    app.config.update(dict(
        SERVER_TYPE=opts.server_type,
        SERVERS=opts.servers or app.config.get('SERVERS'),
        SQLALCHEMY_DATABASE_URI=opts.database_url,
        BASIC_AUTH_USERNAME=opts.username,
        BASIC_AUTH_PASSWORD=opts.password,
        NO_AUTH=opts.no_auth,
        FEED_URI=opts.feed_uri,
        FEED_FORMAT=opts.feed_format,
        EXPORT_URI=opts.export_uri,
    ))
    if opts.verbose:
        app.logger.setLevel(logging.DEBUG)
    initialize()
    app.logger.info("SpiderKeeper startd on %s:%s username:%s/password:%s with %s servers:%s" % (
        opts.host, opts.port, opts.username, opts.password, opts.server_type, ','.join(app.config.get('SERVERS', []))))
    app.run(host=opts.host, port=opts.port, use_reloader=False, threaded=True)


def parse_opts(config):
    parser = OptionParser(usage="%prog [options]",
                          description="Admin ui for spider service")
    parser.add_option("--host",
                      help="host, default:0.0.0.0",
                      dest='host',
                      default='0.0.0.0')
    parser.add_option("--port",
                      help="port, default:5000",
                      dest='port',
                      type="int",
                      default=5000)
    parser.add_option("--username",
                      help="basic auth username ,default: %s" % config.get('BASIC_AUTH_USERNAME'),
                      dest='username',
                      default=config.get('BASIC_AUTH_USERNAME'))
    parser.add_option("--password",
                      help="basic auth password ,default: %s" % config.get('BASIC_AUTH_PASSWORD'),
                      dest='password',
                      default=config.get('BASIC_AUTH_PASSWORD'))
    parser.add_option("--type",
                      help="access spider server type, default: %s" % config.get('SERVER_TYPE'),
                      dest='server_type',
                      default=config.get('SERVER_TYPE'))
    parser.add_option("--server",
                      help="servers, default: %s" % config.get('SERVERS'),
                      dest='servers',
                      action='append',
                      default=[])
    parser.add_option("--database-url",
                      help='SpiderKeeper metadata database default: %s' % config.get('SQLALCHEMY_DATABASE_URI'),
                      dest='database_url',
                      default=config.get('SQLALCHEMY_DATABASE_URI'))
    parser.add_option("--feed-uri",
                      help='FEED_URI scrapy setting, default: %s' % config.get('FEED_URI'),
                      dest='feed_uri',
                      default=config.get('FEED_URI'))
    parser.add_option("--feed-format",
                      help='FEED_FORMAT scrapy setting, default: %s' % config.get('FEED_FORMAT'),
                      dest='feed_format',
                      default=config.get('FEED_FORMAT'))
    parser.add_option("--export-uri",
                      help='Export uri (use if export uri differs from FEED_URI), default: %s' % config.get('EXPORT_URI'),
                      dest='export_uri',
                      default=config.get('EXPORT_URI'))
    parser.add_option("--no-auth",
                      help="disable basic auth",
                      dest='no_auth',
                      action='store_true')
    parser.add_option("-v", "--verbose",
                      help="log level",
                      dest='verbose',
                      action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    main()
