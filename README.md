# SpiderKeeper-2 
### This is a fork of [SpiderKeeper](https://github.com/DormyMo/SpiderKeeper). [Here](https://github.com/kalombos/SpiderKeeper/blob/master/CHANGELOG.md) is the changes

[![Latest Version](http://img.shields.io/pypi/v/SpiderKeeper-2.svg)](https://pypi.python.org/pypi/SpiderKeeper-2)
[![Python Versions](https://img.shields.io/pypi/pyversions/SpiderKeeper-2.svg)](https://pypi.python.org/pypi/SpiderKeeper-2)
![The MIT License](http://img.shields.io/badge/license-MIT-blue.svg)
   
A scalable admin ui for spider service 

## Features

- Manage your spiders from a dashboard. Schedule them to run automatically
- With a single click deploy the scrapy project
- Show spider running stats
- Provide api


Current Support spider service
- [Scrapy](https://github.com/scrapy/scrapy) ( with [scrapyd](https://github.com/scrapy/scrapyd))

## Screenshot
![job dashboard](https://raw.githubusercontent.com/DormyMo/SpiderKeeper/master/screenshot/screenshot_1.png)
![periodic job](https://raw.githubusercontent.com/DormyMo/SpiderKeeper/master/screenshot/screenshot_2.png)
![running stats](https://raw.githubusercontent.com/DormyMo/SpiderKeeper/master/screenshot/screenshot_3.png)

## Getting Started


### Installing


```
pip install spiderkeeper-2
```

### Deployment

``` 

spiderkeeper [options]

Options:

  -h, --help            show this help message and exit
  --host=HOST           host, default:0.0.0.0
  --port=PORT           port, default:5000
  --username=USERNAME   basic auth username ,default: admin
  --password=PASSWORD   basic auth password ,default: admin
  --type=SERVER_TYPE    access spider server type, default: scrapyd
  --server=SERVERS      servers, default: ['http://localhost:6800']
  --database-url=DATABASE_URL
                        SpiderKeeper metadata database default: sqlite:////home/souche/SpiderKeeper.db
  --no-auth             disable basic auth
  -v, --verbose         log level
  

example:

spiderkeeper --server=http://localhost:6800

```

## Usage

```
Visit: 

- web ui : http://localhost:5000

1. Create Project

2. Use [scrapyd-client](https://github.com/scrapy/scrapyd-client) to generate egg file 

   scrapyd-deploy --build-egg output.egg

2. upload egg file (make sure you started scrapyd server)

3. Done & Enjoy it

- api swagger: http://localhost:5000/api.html

``` 

## Authors

- *Initial work* - [DormyMo](https://github.com/DormyMo)
- *Fork author* - [kalombo](https://github.com/kalombos/)


## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcomed!


