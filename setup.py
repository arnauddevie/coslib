#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='coslib',
    version='0.0.0',
    description="CoSLIB is a continuum-scale lithium-ion battery modeling"
    " framework written in Python that utilizes FEniCS and FiPy to solve"
    " finite-element and finite-volume problems.",
    long_description=readme + '\n\n' + history,
    author="Christopher Macklen",
    author_email='cmacklen@uccs.edu',
    url='https://github.com/macklenc/coslib',
    packages=[
        'coslib',
    ],
    package_dir={'coslib':
                 'coslib'},
    entry_points={
        'console_scripts': [
            'coslib=coslib.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='coslib',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
