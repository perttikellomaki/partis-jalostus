from google.appengine.ext import ndb

from HardenedHandler import HardenedHandler
from DatastoreClasses import TerveyskyselyTmp
from DatastoreClasses import Survey

terveyskysely_key = ndb.Key(Survey, 'terveyskysely')

class TerveyskyselyCollectionHandler (HardenedHandler):
    def get_(self, user):
        kysely = terveyskysely_key.get()
        if kysely is None:
            kysely = Survey(key=terveyskysely_key, title="Terveyskysely")
            kysely.Put()
        result = [kysely.hashify()]
        self.jsonReply(result)

class TerveyskyselyTmpCollectionHandler(HardenedHandler):
    def post_(self, user):
        survey = TerveyskyselyTmp()
        survey.populateFromRequest(self.request.params)
        survey.vastaaja = user.nickname()
        survey.vastaaja_id = user.user_id()
        survey.Put()
        survey.koira.get().stampDependentModTime()
        self.jsonReply(survey.hashify())

    def get_(self, user):
        self.genericGetCollection(
            ndb.gql("SELECT * FROM TerveyskyselyTmp where koira = :1 ORDER BY timestamp",
                    self.lookupKey(param='koira')))

TerveyskyselyTmp.collectionHandler(TerveyskyselyTmpCollectionHandler)

