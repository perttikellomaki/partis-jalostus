from google.appengine.ext import ndb
from HardenedHandler import HardenedHandler
from DatastoreClasses import SurveyAnswer, SurveyQuestionAnswer

class SurveyAnswerHandler (HardenedHandler):

    def get_(self, user, key):
        self.genericIndividualPost(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

SurveyAnswer.individualHandler(SurveyAnswerHandler)

class SurveyAnswerCollectionHandler (HardenedHandler):
    def get_(self, user):
        survey = self.lookupKey(param='survey')
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveyAnswer WHERE survey = :1 ORDER BY position",
                    survey))

    def post_(self, user):
        answer = SurveyAnswer()
        answer.populateFromRequest(self.request.Params)
        answer.Put()
        self.jsonReply(answer.hashify())

SurveyAnswer.collectionHandler(SurveyAnswerCollectionHandler)

class SurveyQuestionAnswerHandler (HardenedHandler):

    def get_(self, user, key):
        self.genericIndividualPost(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

SurveyQuestionAnswer.individualHandler(SurveyQuestionAnswerHandler)

class SurveyQuestionAnswerCollectionHandler (HardenedHandler):
    def get_(self, user):
        survey = self.lookupKey(param='survey')
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveyQuestionAnswer WHERE survey = :1 ORDER BY position",
                    survey))

    def post_(self, user):
        answer = SurveyQuestionAnswer()
        answer.populateFromRequest(self.request.Params)
        answer.Put()
        self.jsonReply(answer.hashify())

SurveyQuestionAnswer.collectionHandler(SurveyQuestionAnswerCollectionHandler)
