# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class HomePage(BrowserView):
    index = ViewPageTemplateFile('homepage.pt')

    def __call__(self):
        return self.index()
