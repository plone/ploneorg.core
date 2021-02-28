# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from zope.cachedescriptors.property import Lazy
from plone import api
from random import shuffle
from datetime import datetime


class PremiumProvidersView(BrowserView):
    """ Display premium providers """

    @Lazy
    def get_premium_providers(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='FoundationSponsor',
            sponsorship_type='premium',
            review_state='approved',
            is_provider=True,
            effective={'query': datetime.now(), 'range': 'max'},
            expires={'query': datetime.now(), 'range': 'min'}
        )
        result_list = list(result)
        shuffle(result_list)
        return result_list


class StandardProvidersView(BrowserView):
    """ Display standard providers """

    @Lazy
    def get_standard_providers(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='FoundationSponsor',
            sponsorship_type='standard',
            review_state='approved',
            is_provider=True,
            effective={'query': datetime.now(), 'range': 'max'},
            expires={'query': datetime.now(), 'range': 'min'}
        )
        result_list = list(result)
        shuffle(result_list)
        return result_list


class BasicProvidersView(BrowserView):
    """ Display basic providers """

    @Lazy
    def get_basic_providers(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='FoundationSponsor',
            sponsorship_type='basic',
            review_state='approved',
            is_provider=True,
            effective={'query': datetime.now(), 'range': 'max'},
            expires={'query': datetime.now(), 'range': 'min'}
        )
        result_list = list(result)
        shuffle(result_list)
        return result_list

