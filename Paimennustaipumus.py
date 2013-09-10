from HardenedHandler import HardenedHandler
from DatastoreClasses import YhdistysPaimennustaipumus

class YhdistysPaimennustaipumusCollectionHandler(HardenedHandler):
    def get_(self, user):
        koira = self.lookupKey(param='koira')
        self.genericGetCollection(
            YhdistysPaimennustaipumus.gql("WHERE koira = :1 AND archive_copy_of = NULL",
                                  koira))

    def post_(self, user):
        test = YhdistysPaimennustaipumus()
        test.populateFromRequest(self.request.params)
        test.sign(user)
        test.put()
        self.jsonReply(test.hashify())

YhdistysPaimennustaipumus.collectionHandler(YhdistysPaimennustaipumusCollectionHandler)

class YhdistysPaimennustaipumusHandler(HardenedHandler):
    def post_(self, user, key):
        test = self.lookupKey(urlsafe=key).get()
        test.populateFromRequest(self.request.params)
        test.sign(user)
        test.put()
        self.jsonReply(test.hashify())

YhdistysPaimennustaipumus.individualHandler(YhdistysPaimennustaipumusHandler)
