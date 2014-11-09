import logging
from google.appengine.ext import ndb
from HardenedHandler import HardenedHandler
from DatastoreClasses import Survey, SurveyQuestion

class SurveyQuestionIdSequence(ndb.Model):
    num = ndb.IntegerProperty(default=0)

question_id_key = ndb.Key(SurveyQuestionIdSequence, 'counter')

@ndb.transactional
def get_next_id():
    next_number = question_id_key.get()    
    if next_number is None:
        next_number = SurveyQuestionIdSequence(key=question_id_key, num=0)
        next_number.put()
    next_number.num += 1
    next_number.put()
    return next_number.num

class SurveyHandler (HardenedHandler):
    def get_(self, user, key):
        self.genericIndividualGet(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

Survey.individualHandler(SurveyHandler)

class SurveyCollectionHandler (HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('working_copy_of'):
            original = self.lookupKey(param='working_copy_of')
            self.genericGetCollection(
                ndb.gql("SELECT __key__ FROM Survey WHERE working_copy_of = :1",
                        original))
        else:
            self.genericGetCollection(Survey.query())

    def post_(self, user):
        survey = Survey()
        survey.populateFromRequest(self.request.Params)
        survey.Put()
        self.jsonReply(survey.hashify())

Survey.collectionHandler(SurveyCollectionHandler)

class SurveyQuestionHandler (HardenedHandler):

    def get_(self, user, key):
        self.genericIndividualGet(user, key)

    def post_(self, user, key):
        self.genericIndividualPost(user, key)

SurveyQuestion.individualHandler(SurveyQuestionHandler)

class SurveyQuestionCollectionHandler (HardenedHandler):
    def get_(self, user):
        survey = self.lookupKey(param='survey')
        self.genericGetCollection(
            ndb.gql("SELECT __key__ FROM SurveyQuestion WHERE survey = :1 ORDER BY position",
                    survey))

    def post_(self, user):
        question = SurveyQuestion()
        question.populateFromRequest(self.request.Params)
        question.question_id = get_next_id()
        question.Put()
        logging.info("stored %s" % question)
        self.jsonReply(question.hashify())

SurveyQuestion.collectionHandler(SurveyQuestionCollectionHandler)
