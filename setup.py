# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup
from pip.req import parse_requirements

setup(
    name='msg_topgen',
    version='0.1.1',
    packages=['msg_topgen'],
    entry_points={
        "console_scripts": ['msg_topgen = msg_topgen.msg_topgen:main']
    },
    license='Apache 2.0',
    description='',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    url='https://github.com/rh-messaging-qe/qpid_generator',
    author='Dominik Lenoch <dlenoch@redhat.com>, Jakub Stejskal <jstejska@redhat.com>',
    author_email='jstejska@redhat.com'
)
