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
        'aniso8601==1.2.0',
        'APScheduler==3.3.1',
        'click==6.7',
        'demjson==2.2.4',
        'Flask==0.12.1',
        'Flask-BasicAuth==0.2.0',
        'Flask-RESTful==0.3.5',
        'flask-restful-swagger==0.19',
        'Flask-SQLAlchemy==2.2',
        'itsdangerous==0.24',
        'Jinja2==2.9.6',
        'MarkupSafe==1.0',
        'PyMySQL==0.7.11',
        'python-dateutil==2.6.0',
        'pytz==2017.2',
        'requests==2.13.0',
        'six==1.10.0',
        'SQLAlchemy==1.1.9',
        'tzlocal==1.3',
        'Werkzeug==0.12.1'
    ],

    entry_points={
        'console_scripts': {
            'spiderkeeper = SpiderKeeper.run:main'
        },
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
)
