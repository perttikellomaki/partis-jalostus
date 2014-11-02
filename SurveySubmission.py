from google.appengine.ext import ndb
from google.appengine.ext import deferred
from HardenedHandler import HardenedHandler
from DatastoreClasses import SurveySubmission, SurveyAnswer, SurveyAnswerSummary

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

def recordAnswer(answer_key):
    answer = answer_key.get()
    query = ndb.gql("SELECT __key__ from SurveyAnswerSummary WHERE survey_question = :1 AND year = :2",
                    answer.survey_question, answer.year)
    if query.count() == 0:
        summary = SurveyAnswerSummary(survey_question = answer.survey_question,
                                      year = answer.year,
                                      answer_count = 0,
                                      yes_count = 0,
                                      no_count = 0)
    else:
        summary = query.get()

    summary.answer_count = summary.answer_count + 1
    if answer.yesno_answer is not None:
        if answer.yesno_answer:
            summary.yes_count = summary.yes_count + 1
        else:
            summary.no_count = summary.no_count + 1

    summary.Put()

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
        deferred.defer(recordAnswer, answer.key)
        self.jsonReply(answer.hashify())

SurveyAnswer.collectionHandler(SurveyAnswerCollectionHandler)
