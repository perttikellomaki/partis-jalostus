from google.appengine.ext import ndb

from HardenedHandler import HardenedHandler
from DatastoreClasses import Survey, TerveyskyselySubmission

terveyskysely_key = ndb.Key(Survey, 'terveyskysely')

class TerveyskyselyCollectionHandler (HardenedHandler):
    def get_(self, user):
        kysely = terveyskysely_key.get()
        if kysely is None:
            kysely = Survey(key=terveyskysely_key, title="Terveyskysely")
            kysely.Put()
        result = [kysely.hashify()]
        self.jsonReply(result)

class TerveyskyselySubmissionCollectionHandler (HardenedHandler):
    def get_(self, user):
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM TerveyskyselySubmission"))

    def post_(self, user):
        answer = TerveyskyselySubmission()
        answer.populateFromRequest(self.request.Params)
        answer.Put()
        self.jsonReply(answer.hashify())

TerveyskyselySubmission.collectionHandler(TerveyskyselySubmissionCollectionHandler)

class TerveyskyselySubmissionHandler (HardenedHandler):
    def get_(self, user, key):
        self.genericIndividualGet(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

TerveyskyselySubmission.individualHandler(TerveyskyselySubmissionHandler)
