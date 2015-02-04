from setuptools import setup, find_packages

setup(name='rangehttpserver',
      version='1.0.0',
      description='SimpleHTTPServer with support for Range requests',
      long_description=(
      '''Drop-in replacement for SimpleHTTPServer with support for HTTP Range requests.

      Usage:

          pip install rangehttpserver
          python -m RangeHTTPServer
'''),
      author='Dan Vanderkam',
      author_email='danvdk@gmail.com',
      url='https://github.com/danvk/RangeHTTPServer/',
      packages=['.'],
      install_requires=[],
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License'
      ]
)
