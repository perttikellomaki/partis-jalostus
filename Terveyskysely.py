from google.appengine.ext import ndb

from HardenedHandler import HardenedHandler
from DatastoreClasses import Survey, TerveyskyselyAnswer

terveyskysely_key = ndb.Key(Survey, 'terveyskysely')

class TerveyskyselyCollectionHandler (HardenedHandler):
    def get_(self, user):
        kysely = terveyskysely_key.get()
        if kysely is None:
            kysely = Survey(key=terveyskysely_key, title="Terveyskysely")
            kysely.Put()
        result = [kysely.hashify()]
        self.jsonReply(result)

class TerveyskyselyAnswerCollectionHandler (HardenedHandler):
    def get_(self, user):
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM TerveyskyselyAnswer"))

    def post_(self, user):
        answer = TerveyskyselyAnswer()
        answer.populateFromRequest(self.request.Params)
        answer.Put()
        self.jsonReply(answer.hashify())

TerveyskyselyAnswer.collectionHandler(TerveyskyselyAnswerCollectionHandler)

class TerveyskyselyAnswerHandler (HardenedHandler):
    def get_(self, user, key):
        self.genericIndividualGet(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

TerveyskyselyAnswer.individualHandler(TerveyskyselyAnswerHandler)
