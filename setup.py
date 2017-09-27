# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup
from pip.req import parse_requirements

setup(
    name='qpid_generator',
    version='0.1.1',
    packages=['qpid_generator'],
    entry_points={
        "console_scripts": ['qpid_generator = qpid_generator.qpid_generator:main']
    },
    license='Apache 2.0',
    description='',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    url='https://github.com/rh-messaging-qe/qpid_generator',
    author='Dominik Lenoch <dlenoch@redhat.com>, Jakub Stejskal <jstejska@redhat.com>',
    author_email='jstejska@redhat.com'
)
