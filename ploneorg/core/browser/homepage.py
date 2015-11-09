# -*- coding: utf-8 -*-
from Products.Five import BrowserView

from datetime import datetime
from plone import api


class HomePage(BrowserView):

    def get_events(self):
        pc = api.portal.get_tool('portal_catalog')
        results = pc.searchResults(
            portal_type='Event',
            end={'query': datetime.now(), 'range': 'min'},
            sort_on='start',
            review_state='published'
        )
        return [i.getObject() for i in results[:4]]

    def get_news(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='News Item',
            sort_on='Date',
            sort_order='reverse',
            review_state='published'
        )
        return result[:4]

    def get_sponsors(self):
        # pc = api.portal.get_tool('portal_catalog')
        # # TODO: Filter on type `premium` sponsors.
        # result = pc.searchResults(
        #     portal_type='Sponsor',
        #     sort_on='title',
        #     review_state='published'
        # )
        # return result
        return [
            {'title': 'AcmeCorp'},
            {'title': 'AcmeCorp'},
            {'title': 'AcmeCorp'},
        ]
