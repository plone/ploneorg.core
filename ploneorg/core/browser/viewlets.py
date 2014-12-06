# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase


class HeroImage(ViewletBase):

    index = ViewPageTemplateFile("heroimage.pt")

    # def update(self):
    #     super(DocumentActionsViewlet, self).update()
