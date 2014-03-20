from google.appengine.ext import ndb

from HardenedHandler import HardenedHandler
from DatastoreClasses import TerveyskyselyTmp

class TerveyskyselyTmpCollectionHandler(HardenedHandler):
    def post_(self, user):
        survey = TerveyskyselyTmp()
        survey.populateFromRequest(self.request.params)
        survey.Put()
        self.jsonReply(survey.hashify())

    def get_(self, user):
        self.genericGetCollection(
            ndb.gql("SELECT * FROM TerveyskyselyTmp where koira = :1",
                    self.lookupKey(param='koira')))

TerveyskyselyTmp.collectionHandler(TerveyskyselyTmpCollectionHandler)

