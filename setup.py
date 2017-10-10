# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session='hack')

# reqs is a list of requirement
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='msg_topgen',
    version='0.1.2',
    packages=['msg_topgen'],
    entry_points={
        "console_scripts": ['msg_topgen = msg_topgen.msg_topgen:main']
    },
    license='Apache 2.0',
    description='',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=reqs,
    url='https://github.com/rh-messaging-qe/qpid_generator',
    author='Dominik Lenoch <dlenoch@redhat.com>, Jakub Stejskal <jstejska@redhat.com>',
    author_email='jstejska@redhat.com'
)
