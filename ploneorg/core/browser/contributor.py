from Products.Five import BrowserView

class ContributorView(BrowserView):
    
    def cover(self):
        return "%s/@@download/cover" % self.context.absolute_url()