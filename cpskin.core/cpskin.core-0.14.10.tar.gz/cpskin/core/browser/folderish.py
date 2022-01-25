from collective.folderishtypes.browser.viewlets import ListingViewlet


class FolderishViewlet(ListingViewlet):

    def available(self):
        return False
