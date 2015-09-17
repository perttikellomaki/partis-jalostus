import time
import dateutil
import dateutil.parser
import logging
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
import Util
from UriAddressable import UriAddressable, field

class KoiraAutocomplete(ndb.Model):
    virallinen_nimi = ndb.StringProperty()
    canonical = ndb.StringProperty()
    uros = ndb.BooleanProperty()

class SignedResource(UriAddressable):
    d = dict(UriAddressable.d.items())

    author =       field(d, 'author', ndb.StringProperty())
    author_nick =  field(d, 'author_nick', ndb.StringProperty())
    author_email = field(d, 'author_email', ndb.StringProperty())
    verified     = field(d, 'verified', ndb.BooleanProperty(), readonly=True)

    # archive_copy_of is intentionally not defined using field()
    archive_copy_of = ndb.KeyProperty()

                    
    def subsumes(self, item):
        """Return true if self is signed by the same user, and
        the information contained in self is a superset of the
        information in item."""

        for name, info in self.fields().items():
            if name != 'timestamp':
                field, uri_prefix, _, _ = info
                my_val = field.__get__(self, type(self))
                item_val = field.__get__(item, type(item))
                if my_val == item_val:
                    # value not touched
                    pass
                elif my_val != None and item_val == None:
                    # my_val was set
                    pass
                else:
                    logging.info("subsumes: conflicting values found %s and %s" % (my_val, item_val))
                    # there were conflicting values
                    return False

        # no conflicting values found    
        return True

    def sign(self, user, request=None, dog_key=None):
        self.author = str(user.user_id())
        self.author_nick = user.nickname()
        self.author_email = user.email()

        if request and request.params.has_key('verified'):
            if users.is_current_user_admin():
                self.verified = True
            else:
                kennel = Kennel.gql("WHERE kasvattaja_email = :1",
                                    self.author_email)
                if kennel.count() > 0:
                    self.verified = (dog_key.get().kennel
                                     == kennel.get().nimi)

    def archive_fields(self, copy):
        for name, info in self.fields().items():
            prop, _, _, _, _, _, _ = info
            prop.__set__(copy, prop.__get__(self, type(self)))
        copy.archive_copy_of = self.key
        return copy


class Koira(ndb.Model, SignedResource):
    d = dict(SignedResource.d.items())
    virallinen_nimi = field(d, 'virallinen_nimi', ndb.StringProperty())
    kutsumanimi =     field(d, 'kutsumanimi', ndb.StringProperty())
    kennel =          field(d, 'kennel', ndb.StringProperty())
    sukupuoli =       field(d, 'sukupuoli', ndb.StringProperty())
    syntymapaiva =    field(d, 'syntymapaiva', ndb.DateProperty())
    syntymavuosi =    field(d, 'syntymavuosi', ndb.IntegerProperty())
    isa =             field(d, 'isa', ndb.KeyProperty(), uri_prefix="/Koira")
    ema =             field(d, 'ema', ndb.KeyProperty(), uri_prefix="/Koira")
    canonical_name =  field(d, 'canonical_name', ndb.StringProperty())

    def archive(self):
        """Create archival copy"""
        copy = Koira()
        return self.archive_fields(copy)

    def useModTime(self):
        return True

class YhdistysPaimennustaipumus(ndb.Model, SignedResource):
    d = dict(SignedResource.d.items())
    koira =              field(d, 'koira', ndb.KeyProperty(), uri_prefix="/Koira")
    hyvaksytty =         field(d, 'hyvaksytty', ndb.BooleanProperty())
    kiinnostus =         field(d, 'kiinnostus', ndb.IntegerProperty())
    taipumus =           field(d, 'taipumus', ndb.IntegerProperty())
    henkinen_kestavyys = field(d, 'henkinen_kestavyys',  ndb.IntegerProperty())
    ohjattavuus =        field(d, 'ohjattavuus', ndb.IntegerProperty())
    tuomari =            field(d, 'tuomari', ndb.StringProperty())
    paikka =             field(d, 'paikka', ndb.StringProperty())
    paiva =              field(d, 'paiva', ndb.DateProperty())
    kommentit =          field(d, 'kommentit', ndb.StringProperty())

    def archive(self):
        """Create archival copy"""
        copy = YhdistysPaimennustaipumus()
        return self.archive_fields(copy)

class Kennels (ndb.Model, UriAddressable):
    """Singleton object to hold modtime for kennels."""
    d = dict(UriAddressable.d.items())

    @staticmethod
    def getSingleton():

        def get_or_insert():
            key = ndb.Key(Kennels, 'kennels')
            p = key.get()
            if p is None:
                p = Kennels(id = 'kennels')
                p.Put()
                return p.key
            else:
                return key
            
        return ndb.transaction(lambda: get_or_insert())



class Kennel (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    nimi =             field(d, 'nimi', ndb.StringProperty())
    kasvattaja_email = field(d, 'kasvattaja_email', ndb.StringProperty())
    canonical_name = ndb.StringProperty()

class ChangeNotification (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    kennel =         field(d, 'kennel', ndb.StringProperty())
    is_creation =    field(d, 'is_creation', ndb.BooleanProperty())  # true if entity was created
    koira =          field(d, 'koira', ndb.KeyProperty())
    changed_entity = field(d, 'changed_entity', ndb.KeyProperty())
    author_nick =    field(d, 'author_nick', ndb.StringProperty())

class Survey (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    title = field(d, 'title', ndb.StringProperty())
    working_copy_of = field(d, 'working_copy_of', ndb.KeyProperty())

class SurveyQuestion (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    question_id = field(d, 'question_id', ndb.IntegerProperty())
    male_only = field(d, 'male_only', ndb.BooleanProperty())
    female_only = field(d, 'female_only', ndb.BooleanProperty())
    survey = field(d, 'survey', ndb.KeyProperty())
    question = field(d, 'question', ndb.TextProperty())
    detail_question = field(d, 'detail_question', ndb.TextProperty())
    position = field(d, 'position', ndb.IntegerProperty(required=True, default=0))
    question_kind = field(d, 'question_kind', ndb.StringProperty())
    working_copy_of = field(d, 'working_copy_of', ndb.KeyProperty())

class SurveySubmission (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    survey = field(d, 'survey', ndb.KeyProperty())
    created = field(d, 'created', ndb.DateTimeProperty(auto_now_add=True))
    year = field(d, 'year', ndb.IntegerProperty())
    email = field(d, 'email', ndb.StringProperty())

class SurveySubmissionSummary (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    survey = field(d, 'survey', ndb.KeyProperty())
    year = field(d, 'year', ndb.IntegerProperty())
    answer_count = field(d, 'answer_count', ndb.IntegerProperty(default=0))

class SurveyAnswer (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())

    # The SurveySubmission this answer is part of.
    survey_submission = field(d, 'survey_submission', ndb.KeyProperty())

    # The SurveyQuestion being answered.
    survey_question = field(d, 'survey_question', ndb.KeyProperty())

    # The position of the question is copied here so we can retrieve
    # answers in the order the questions were asked.
    position = field(d, 'position', ndb.IntegerProperty())

    yesno_answer =  field(d, 'yesno_answer', ndb.BooleanProperty())
    free_text_answer = field(d, 'free_text_answer', ndb.TextProperty())

    created = field(d, 'created', ndb.DateTimeProperty(auto_now_add=True))
    year = field(d, 'year', ndb.IntegerProperty())

class SurveyAnswerSummary (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    survey_question = field(d, 'survey_question', ndb.KeyProperty())
    year = field(d, 'year', ndb.IntegerProperty())
    answer_count = field(d, 'answer_count', ndb.IntegerProperty(default=0))
    yes_count = field(d, 'yes_count', ndb.IntegerProperty(default=0))
    no_count = field(d, 'no_count', ndb.IntegerProperty(default=0))


class TerveyskyselySubmission (SurveySubmission):
    d = dict(SurveySubmission.d.items())
    koira = field(d, 'koira', ndb.KeyProperty())
    dog_name = field(d, 'dog_name', ndb.StringProperty())
    owner_confirmed = field(d, 'owner_confirmed', ndb.BooleanProperty())
    answered_by = field(d, 'answered_by', ndb.KeyProperty())

    # The confirmation code is set if the user was not signed in.
    # Boolean submitter_confirmed is also set to false, and
    # it is set to true once the user clicks on an emailed link.
    confirmation_code = ndb.StringProperty()
    submitter_confirmed = field(d, 'submitter_confirmed', ndb.BooleanProperty(default=True))

class Role (polymodel.PolyModel, UriAddressable):
    d = dict(UriAddressable.d.items())
    user_id = field(d, 'user_id', ndb.StringProperty())
    role = field(d, 'role', ndb.StringProperty())
    valid = field(d, 'valid', ndb.BooleanProperty())
    confirmed_by = field(d, 'confirmed_by', ndb.KeyProperty())

class DogOwnerRole (Role):
    d = dict(Role.d.items())
    owner_name = field(d, 'owner_name', ndb.StringProperty())
    dog = field(d, 'dog', ndb.KeyProperty())

class Profile (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    user_id = field(d, 'user_id', ndb.StringProperty())
    nickname = field(d, 'nickname', ndb.StringProperty())

    @staticmethod
    def byUser (user):
        return ndb.Key('Profile', user.user_id())

    @staticmethod
    def byUserId (user_id):
        return ndb.Key('Profile', user_id)

