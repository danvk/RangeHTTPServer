from setuptools import setup

with open('README', encoding='utf8') as fh:
    long_description = fh.read()

setup(name='rangehttpserver',
      version='1.4.0',
      description='SimpleHTTPServer with support for Range requests',
      long_description=long_description,
      long_description_content_type='text/markdown',
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
