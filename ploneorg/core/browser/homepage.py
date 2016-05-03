# -*- coding: utf-8 -*-
from Products.Five import BrowserView

from datetime import datetime
from plone import api
from random import shuffle

class HomePage(BrowserView):

    def get_links(self):
        pc = api.portal.get_tool('portal_catalog')
        links = pc.searchResults(
            portal_type="site_link",
            review_state='published'
        )
        return [i.getObject() for i in links]

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
        portal = api.portal.get()
        front_page_news = portal['news']['front-page-news']
        result = front_page_news.results(brains=True)
        return result

    def get_sponsors(self):
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(
            portal_type='Image',
            Subject=['sponsor logo'],
        )
        result_list = list(result)
        random.shuffle(result_list)
        return result_list
