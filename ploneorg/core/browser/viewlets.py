from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from zope.cachedescriptors.property import Lazy


class LinkViewlet(ViewletBase):

    @Lazy
    def get_links(self):
        pc = api.portal.get_tool('portal_catalog')
        portal = api.portal.get()
        links = pc.searchResults(
            container=portal['related-websites'],
            portal_type="site_link",
            review_state='published'
        )
        objects = [i.getObject() for i in links]
        return [i for i in objects if i.display_in_top_bar]
