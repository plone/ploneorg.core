# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from zope.cachedescriptors.property import Lazy
from plone import api
from random import shuffle
from datetime import datetime


class PremiumSponsorsView(BrowserView):
    """ Display premium sponsors """

    @Lazy
    def get_premium_sponsors(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='FoundationSponsor',
            sponsorship_type='premium',
            review_state='approved',
            effective={'query': datetime.now(), 'range': 'max'},
            expires={'query': datetime.now(), 'range': 'min'}
        )
        result_list = list(result)
        shuffle(result_list)
        return result_list


class StandardSponsorsView(BrowserView):
    """ Display standard sponsors """

    @Lazy
    def get_standard_sponsors(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='FoundationSponsor',
            sponsorship_type='standard',
            review_state='approved',
            effective={'query': datetime.now(), 'range': 'max'},
            expires={'query': datetime.now(), 'range': 'min'}
        )
        result_list = list(result)
        shuffle(result_list)
        return result_list


class UniversitySponsorsView(BrowserView):
    """ Display university sponsors """

    @Lazy
    def get_university_sponsors(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='FoundationSponsor',
            sponsorship_type='university',
            review_state='approved',
            effective={'query': datetime.now(), 'range': 'max'},
            expires={'query': datetime.now(), 'range': 'min'}
        )
        result_list = list(result)
        shuffle(result_list)
        return result_list

