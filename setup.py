# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup

setup(
    name='msg_topgen',
    version='0.1.12',
    packages=['msg_topgen'],
    entry_points={
        "console_scripts": ['msg_topgen = msg_topgen.msg_topgen:main']
    },
    license='Apache 2.0',
    description='',
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'nose'
    ],
    install_requires=[
        'networkx==2.0',
        'PyYAML>=3.12',
        'ansible>=2.3.2.0',
        'libracmp',
        'matplotlib',
        'argparse'
    ],
    url='https://github.com/rh-messaging-qe/qpid_generator',
    author='Dominik Lenoch <dlenoch@redhat.com>, Jakub Stejskal <jstejska@redhat.com>',
    author_email='jstejska@redhat.com'
)
