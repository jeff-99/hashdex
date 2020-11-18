#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.7'
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner>=2.12',
    # TODO(jeff-99): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest>=3.2',
    'pytest-mock>=1.6'
    # TODO: put package test requirements here
]

setup(
    name='hashdex',
    version='0.7.0',
    description="A file indexer based on content hashes",
    long_description=readme + '\n\n' + history,
    author="Jeffrey Slort",
    author_email='j_slort@hotmail.com',
    url='https://github.com/jeff-99/hashdex',
    packages=find_packages(include=['hashdex']),
    entry_points={
        'console_scripts': [
            'hashdex=hashdex.cli:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='hashdex',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
