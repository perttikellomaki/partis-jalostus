from google.appengine.ext import ndb

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

class SurveyAnswerHandler (HardenedHandler):

    def get_(self, user, key):
        self.genericIndividualPost(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

SurveyAnswer.individualHandler(SurveyAnswerHandler)

@ndb.transactional
def recordAnswer(summary_key, answer):
    summary = summary_key.get()
    summary.survey_question = answer.survey_question
    summary.year = answer.year
    if answer.yesno_answer is not None or (answer.free_text_answer is not None and len(answer.free_text_answer) > 0):
        summary.answer_count = summary.answer_count + 1
    if answer.yesno_answer is not None:
        if answer.yesno_answer:
            summary.yes_count = summary.yes_count + 1
        else:
            summary.no_count = summary.no_count + 1
    summary.put()


class SurveyAnswerCollectionHandler (HardenedHandler):
    def get_(self, user):
        survey_submission = self.lookupKey(param='survey_submission')
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveyAnswer WHERE survey_submission = :1 ORDER BY position",
                    survey_submission))

    def post_unauthenticated_(self):
        self.post_(None)

    def post_(self, user):
        answer = SurveyAnswer()
        answer.populateFromRequest(self.request.Params)
        answer.Put()

        summary = SurveyAnswerSummary.get_or_insert("%s" % answer.year, parent=answer.survey_question)

        if user:
            recordAnswer(summary.key, answer)

        self.jsonReply(answer.hashify())

SurveyAnswer.collectionHandler(SurveyAnswerCollectionHandler)

class SurveyAnswerSummaryCollectionHandler (HardenedHandler):

    def get_(self, user):
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveyAnswerSummary WHERE survey_question = :1",
                    self.lookupKey(param='survey_question')))


SurveyAnswerSummary.collectionHandler(SurveyAnswerSummaryCollectionHandler)
