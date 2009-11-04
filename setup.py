from setuptools import setup, find_packages
import os

name = 'chaoflow.os.cmdlets'
version = '0.1'

setup(name=name,
      version=version,
      description='Easy, pain- and noise-free execution of cmdlines',
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      keywords='',
      author='Florian Friesdorf',
      author_email='flo@chaoflow.net',
      url='http://github.com/chaoflow/chaoflow.git.porcelain',
      license='LGPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['chaoflow','chaoflow.os'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'interlude',
              'chaoflow.testing.crawler',
              ],
          },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
