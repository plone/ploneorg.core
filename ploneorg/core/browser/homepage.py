# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime
from plone import api


class HomePage(BrowserView):
    index = ViewPageTemplateFile('homepage.pt')

    def __call__(self):
        return self.index()

    def get_events(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(portal_type='Event',
                                  end={'query': datetime.now(), 'range': 'min'},
                                  sort_on='start',
                                  review_state='published')

        return result[:4]

    def get_news(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(portal_type='News Item',
                                  sort_on='Date',
                                  sort_order='reverse',
                                  review_state='published')
        return result[:4]
