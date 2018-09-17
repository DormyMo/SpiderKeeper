#!/usr/bin/env python

from setuptools import setup, find_packages

from SpiderKeeper import __version__, __author__

setup(
    name='SpiderKeeper-2',
    version=__version__,
    description='Admin ui for spider service',
    long_description=
    'Go to https://github.com/kalombos/SpiderKeeper/ for more information.',
    author=__author__,
    author_email='nogamemorebrain@gmail.com',
    url='https://github.com/kalombos/SpiderKeeper/',
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'APScheduler==3.5.3',
        'Flask==1.0.2',
        'Flask-BasicAuth==0.2.0',
        'Flask-RESTful==0.3.6',
        'flask-restful-swagger==0.20.1',
        'Flask-SQLAlchemy==2.3.2',
        'demjson==2.2.4',
        'requests==2.19.1',
        'scrapyd'
    ],

    entry_points={
        'console_scripts': {
            'spiderkeeper = SpiderKeeper.scrapyd.scripts.scrapyd_run:main'
        },
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
)
