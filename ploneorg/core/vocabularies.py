# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import pycountry


countries = [SimpleTerm(value=country.alpha3,
                        token=country.alpha3,
                        title=country.name)
             for country in pycountry.countries]
country_vocabulary = SimpleVocabulary(countries)


platforms = [u'all platforms', u'Mac OS X', u'Windows', u'Linux/BSD/Unix']
platform_vocabulary = SimpleVocabulary(
    [
        SimpleTerm(
            value=a,
            token=a,
            title=a)
        for a in platforms
    ]
)
