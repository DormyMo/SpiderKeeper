import logging
import os
from optparse import OptionParser

from SpiderKeeper.app import app, initialize


def main():
    opts, args = parse_opts()
    app.config.update(dict(
        SERVER_TYPE=opts.server_type,
        SERVERS=opts.servers or ['http://localhost:6800'],
        SQLALCHEMY_DATABASE_URI=opts.database_url
    ))
    if opts.verbose:
        app.logger.setLevel(logging.DEBUG)
    initialize()
    app.logger.info("SpiderKeeper startd on %s:%s with %s servers:%s" % (
        opts.host, opts.port, opts.server_type, ','.join(app.config.get('SERVERS', []))))
    app.run(host=opts.host, port=opts.port, use_reloader=False, threaded=True)


def parse_opts():
    parser = OptionParser(usage="%prog [options]",
                          description="Admin ui for spider service")
    parser.add_option("--type",
                      help="access spider server type, default:scrapyd",
                      dest='server_type',
                      default='scrapyd')
    parser.add_option("--host",
                      help="host, default:0.0.0.0",
                      dest='host',
                      default='0.0.0.0')
    parser.add_option("--port",
                      help="port, default:5000",
                      dest='port',
                      type="int",
                      default=5000)
    parser.add_option("--server",
                      help="servers, default:http://localhost:6800",
                      dest='servers',
                      action='append',
                      default=[])
    default_database_url = 'sqlite:///' + os.path.join(os.path.abspath('.'), 'SpiderKeeper.db')
    parser.add_option("--database_url",
                      help='SpiderKeeper metadata database default:' + default_database_url,
                      dest='database_url',
                      default=default_database_url)
    parser.add_option("-v", "--verbose",
                      help="log level",
                      dest='verbose',
                      action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    main()
