from optparse import OptionParser

from app import app


def main():
    opts, args = parse_opts()
    exitcode = 0
    app.config.SERVER_TYPE = opts.server_type
    app.config.SERVERS = opts.servers or ['http://localhost:6800']
    app.run(host=opts.host, port=opts.port, debug=True, threaded=True)


def parse_opts():
    parser = OptionParser(usage="%prog [options]",
                          description="Deploy Scrapy project to Scrapyd server")
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
    return parser.parse_args()


if __name__ == '__main__':
    main()
