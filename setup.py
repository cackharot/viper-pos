import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'setuptools',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_handlers',
    'formencode',
    'pyramid_jinja2',
    'mysql-python',
    'pyramid_simpleform',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'docutils',
    'pastescript',
    ]
    
setup(name='viper',
      version='1.0',
      description='viper',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='cackharot',
      author_email='cackharot@gmail.com',
      url='http://pos.vipersuites.in',
      keywords='pos sales online point of sales openpos python pos erp viper',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='viper',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = viper:main
      [console_scripts]
      initialize_viper_db = viper.scripts.initializedb:main
      """,
      )

