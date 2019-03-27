#!/usr/bin/env python
import os
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='isodate',
      version='0.6.0.dev',
      packages=['isodate', 'isodate.tests'],
      package_dir={'': 'src'},

      # dependencies:
      install_requires=[
          'six'
      ],

      # PyPI metadata
      author='Gerhard Weis',
      author_email='gerhard.weis@proclos.com',
      description='An ISO 8601 date/time/duration parser and formatter',
      license='BSD',
      # keywords = '',
      url='https://github.com/gweis/isodate/',

      long_description=(read('README.rst') +
                        read('CHANGES.txt') +
                        read('TODO.txt')),

      classifiers=['Development Status :: 4 - Beta',
                   # 'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Topic :: Internet',
                   ('Topic :: Software Development :'
                    ': Libraries :: Python Modules'),
                   ],
      test_suite='isodate.tests.test_suite')
