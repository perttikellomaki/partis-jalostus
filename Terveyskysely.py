import uuid

from google.appengine.ext import deferred, ndb
from google.appengine.api import mail

from DatastoreClasses import DogOwnerRole, Profile, Survey, \
    SurveySubmissionSummary, TerveyskyselySubmission
from HardenedHandler import HardenedHandler


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


def processSubmission(user_id, user_name, submission_key):
    # update summary
    submission = submission_key.get()
    summary = SurveySubmissionSummary.get_or_insert("%s" % submission.year, parent=submission.survey)
    recordSubmission(summary.key, submission)

    # create dog ownership if needed
    roles = DogOwnerRole.gql("WHERE role = :1 AND dog = :2 AND user_id = :3 AND valid = true", "dog_owner", submission.koira, user_id)
    if roles.count() == 0:
        role = DogOwnerRole(user_id=user_id, role="dog_owner", 
                            owner_name=user_name, dog=submission.koira, valid=False)
        role.put()
        submission.owner_confirmed = False
    else:
        submission.owner_confirmed = True
        submission.Put()


def requestEmailConfirmation(submission_key):
    submission = submission_key.get()
    mail.send_mail(sender="Partistietokanta <partistietokanta@example.com",
                   to=submission.email,
                   subject="Terveyskyselyn varmistus",
                   body="Kiitos vastauksestasi. Klikkaatko viela oheista linkkia vahvistukseksi. %s" % submission.confirmation_code)

class TerveyskyselySubmissionCollectionHandler (HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('koira'):
            koira = self.lookupKey(param='koira')
            self.genericGetCollection(
                ndb.gql("SELECT __key__ FROM TerveyskyselySubmission WHERE koira = :1 ORDER BY created", koira))
        else:
            self.genericGetCollection(
                ndb.gql("SELECT __key__ FROM TerveyskyselySubmission ORDER BY created"))

    def post_unauthenticated_(self):
        self.post_(None)

    def post_(self, user):
        submission = TerveyskyselySubmission()
        submission.populateFromRequest(self.request.Params)

        if user:
            submission.answered_by = Profile.byUser(user)
        else:
            # Used for validating the submission via email link.
            submission.confirmation_code = uuid.uuid4().hex

        submission.owner_confirmed = False
        submission.Put()

        if user:
            deferred.defer(processSubmission, user.user_id(), user.nickname(), submission.key)
        else:
            deferred.defer(requestEmailConfirmation, submission.key)

        self.jsonReply(submission.hashify())


TerveyskyselySubmission.collectionHandler(TerveyskyselySubmissionCollectionHandler)


class TerveyskyselySubmissionHandler (HardenedHandler):
    def get_(self, user, key):
        self.genericIndividualGet(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

TerveyskyselySubmission.individualHandler(TerveyskyselySubmissionHandler)
