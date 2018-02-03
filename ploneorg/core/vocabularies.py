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

payment_frequency_vocabulary = SimpleVocabulary(
    [
        SimpleTerm(
            value=a,
            token=a,
            title=a)
        for a in [u'annual', u'monthly', u'n/a']
    ]
)

payment_method_vocabulary = SimpleVocabulary(
    [
        SimpleTerm(
            value=a,
            token=a,
            title=a)
        for a in [u'wire', u'check', u'PayPal', u'in kind', u'cash']
    ]
)

sponsorship_type_vocabulary = SimpleVocabulary(
    [
        SimpleTerm(
            value=a,
            token=a,
            title=a)
        for a in [u'premium', u'standard', u'basic', u'university']
    ]
)

currencies = [SimpleTerm(value=currency.letter,
                        token=currency.letter,
                        title=currency.name)
             for currency in pycountry.currencies]
payment_currency_vocabulary = SimpleVocabulary(currencies)

orgsizes = [
    {'token' : u'small', 'value' : u'small', 'name' : u'small (up to and including 2 FTEs)'},
    {'token' : u'medium', 'value' : u'medium', 'name' : u'medium (between 3 and 7 FTEs'},
    {'token' : u'large', 'value' : u'large', 'name' : u'large (more than 7 FTEs)'},
    {'token' : u'university', 'value' : u'university', 'name' : u'university'},
]
orgsizes_terms = [SimpleTerm(value=orgsize['value'],
                             token=orgsize['token'],
                             title=orgsize['name'])
             for orgsize in orgsizes]
org_size_vocabulary = SimpleVocabulary(orgsizes_terms)
