# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '1.0a1'

README = open("README.rst").read()
HISTORY = open("CHANGES.rst").read()

setup(
    name='ploneorg.core',
    version=version,
    description="plone.org Core Package",
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
    extras_require={
        'test': ['plone.app.testing[robot]>=5.0',
                 'plone.app.contenttypes[test]'],
    },
    install_requires=[
        'Products.CMFPlone',
        'Py-StackExchange',
        'PyGithub',
        'collective.monkeypatcher',
        'collective.badge',
        'collective.themefragments',
        'collective.z3cform.datagridfield',
        'launchpadlib',
        'plone.api',
        'plone.app.referenceablebehavior',
        'plone.app.vulnerabilities',
        'plone.directives.form',
        'ploneorg.theme',
        'pycountry',
        'requests',
        'setuptools',
        'simplejson',
        'twitter',
        'plone.app.mosaic',
        'pyquery'
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_contributions = ploneorg.core.contributions:update_contributions
    get_downloads = ploneorg.core.downloads:get_downloads
    """,
)
