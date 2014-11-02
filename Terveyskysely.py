from google.appengine.ext import ndb

from HardenedHandler import HardenedHandler
from DatastoreClasses import Survey, TerveyskyselySubmission, SurveySubmissionSummary

terveyskysely_key = ndb.Key(Survey, 'terveyskysely')

class TerveyskyselyCollectionHandler (HardenedHandler):
    def get_(self, user):
        kysely = terveyskysely_key.get()
        if kysely is None:
            kysely = Survey(key=terveyskysely_key, title="Terveyskysely")
            kysely.Put()
        result = [kysely.hashify()]
        self.jsonReply(result)



@ndb.transactional
def recordSubmission(summary_key, submission):
    summary = summary_key.get()
    summary.survey = submission.survey
    summary.answer_count = summary.answer_count + 1
    summary.year = submission.year
    summary.put()

class TerveyskyselySubmissionCollectionHandler (HardenedHandler):
    def get_(self, user):
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM TerveyskyselySubmission"))

    def post_(self, user):
        submission = TerveyskyselySubmission()
        submission.populateFromRequest(self.request.Params)
        submission.Put()

        summary = SurveySubmissionSummary.get_or_insert("%s" % submission.year, parent=submission.survey)
        recordSubmission(summary.key, submission)

        self.jsonReply(submission.hashify())

TerveyskyselySubmission.collectionHandler(TerveyskyselySubmissionCollectionHandler)

class TerveyskyselySubmissionHandler (HardenedHandler):
    def get_(self, user, key):
        self.genericIndividualGet(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

TerveyskyselySubmission.individualHandler(TerveyskyselySubmissionHandler)
