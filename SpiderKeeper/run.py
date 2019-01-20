from SpiderKeeper.app import app, initialize


def main():
    initialize()
    app.run(host='0.0.0.0', port=5000, threaded=True)


if __name__ == '__main__':
    main()
