# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os

version = '1.0a1'

README = open("README.rst").read()
HISTORY = open(os.path.join("docs", "HISTORY.rst")).read()

setup(
    name='ploneorg.core',
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
    extras_require={
        'test': ['plone.app.testing[robot]>=4.2.2'],
        'migration': ['ploneorg.migration'],
    },
    install_requires=[
        'Py-StackExchange',
        'PyGithub',
        'collective.monkeypatcher',
        'collective.badge',
        'plone.api',
        'plone.app.referenceablebehavior',
        'plone.app.vulnerabilities',
        'plone.directives.form',
        'ploneorg.theme',
        'pycountry',
        'requests',
        'setuptools',
        'twitter',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_contributions = ploneorg.core.contributions:update_contributions
    """,
)
