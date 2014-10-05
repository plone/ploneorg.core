from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class HeroImage(ViewletBase):

    index = ViewPageTemplateFile("heroimage.pt")

    # def update(self):
    #     super(DocumentActionsViewlet, self).update()
