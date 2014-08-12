from setuptools import setup, find_packages
import os

version = '1.0a1'

README = open("README.rst").read()
HISTORY = open(os.path.join("docs", "HISTORY.rst")).read()

setup(name='ploneorg.core',
      version=version,
      description="plone.org 2014 site core",
      long_description=README + "\n" + HISTORY,
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='plone ploneorg diazo theme',
      author='Plone Foundation',
      author_email='foundation@plone.org',
      url='https://github.com/plone/ploneorg.core',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ploneorg'],
      include_package_data=True,
      zip_safe=False,
      extras_require={'test': ['plone.app.testing[robot]>=4.2.2']},
      install_requires=[
          'setuptools',
          'ploneorg.theme',
          'plone.api',
          'plone.app.contenttypes',
          'plone.app.event[dexterity]',
          'plone.app.widgets[dexterity]',
          'wildcard.foldercontents',
          'collective.monkeypatcher',
          'PyGithub',
          'requests',
          'pycountry',
          'plone.formwidget.multifile',
          'Py-StackExchange'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      [console_scripts]
      update_contributions = ploneorg.core.contributions:update_contributions
      """,
      )
