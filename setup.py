from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc = 'Soundcloud RESTful Python Client based on restkit.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
tests_require = ['interlude']

setup(name='soundcloudapi',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Software Development',       
            'License :: OSI Approved :: BSD License',
      ],
      keywords='',
      author='Jens Klein',
      author_email='dev@bluedynamics.com',
      url=u'http://github.com/bluedynamics/soundcloudapi',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
            'setuptools',
            'restkit',
      ],
      tests_require=tests_require,
      test_suite="soundcloudapi.tests.test_suite",
      extras_require = dict(
          test=tests_require,
      ),
)
