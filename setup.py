from setuptools import setup

setup(name='rangehttpserver',
      version='1.3.0',
      description='SimpleHTTPServer with support for Range requests',
      author='Dan Vanderkam',
      author_email='danvdk@gmail.com',
      url='https://github.com/danvk/RangeHTTPServer/',
      packages=['RangeHTTPServer'],
      install_requires=[],
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License'
      ]
)
