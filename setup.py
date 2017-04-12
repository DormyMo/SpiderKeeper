#!/usr/bin/env python

from setuptools import setup, find_packages

from SpiderKeeper import __version__, __author__

setup(
    name='SpiderKeeper',
    version=__version__,
    description='Admin ui for spider service',
    long_description=
    'Go to https://github.com/DormyMo/SpiderKeeper/ for more information.',
    author=__author__,
    author_email='modongming91@gmail.com',
    url='https://github.com/DormyMo/SpiderKeeper/',
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'APScheduler==3.3.1',
        'Flask==0.12.1',
        'Flask-RESTful==0.3.5',
        'flask-restful-swagger==0.19',
        'Flask-SQLAlchemy==2.2',
        'PyMySQL==0.7.11',
        'requests==2.13.0'
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
        'Programming Language :: Python :: 3',
    ],
)
