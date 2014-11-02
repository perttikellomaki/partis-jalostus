from google.appengine.ext import ndb
from HardenedHandler import HardenedHandler
from DatastoreClasses import SurveySubmission, SurveyAnswer

class SurveySubmissionHandler (HardenedHandler):

    def get_(self, user, key):
        self.genericIndividualPost(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

SurveySubmission.individualHandler(SurveySubmissionHandler)

class SurveySubmissionCollectionHandler (HardenedHandler):
    def get_(self, user):
        survey = self.lookupKey(param='survey')
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveySubmission WHERE survey = :1 ORDER BY position",
                    survey))

    def post_(self, user):
        submission = SurveySubmission()
        submission.populateFromRequest(self.request.Params)
        submission.Put()
        self.jsonReply(submission.hashify())

SurveySubmission.collectionHandler(SurveySubmissionCollectionHandler)

class SurveyAnswerHandler (HardenedHandler):

    def get_(self, user, key):
        self.genericIndividualPost(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

SurveyAnswer.individualHandler(SurveyAnswerHandler)

class SurveyAnswerCollectionHandler (HardenedHandler):
    def get_(self, user):
        survey_submission = self.lookupKey(param='survey_submission')
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveyAnswer WHERE survey_submission = :1 ORDER BY position",
                    survey_submission))

    def post_(self, user):
        answer = SurveyAnswer()
        answer.populateFromRequest(self.request.Params)
        answer.Put()
        self.jsonReply(answer.hashify())

SurveyAnswer.collectionHandler(SurveyAnswerCollectionHandler)
