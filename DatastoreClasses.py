import time
import dateutil
import dateutil.parser
import logging
from google.appengine.api import users
from google.appengine.ext import ndb
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

class TerveyskyselyTmp (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    koira = field(d, 'koira', ndb.KeyProperty())
    koira_virallinen_nimi = field(d, 'koira_virallinen_nimi', ndb.StringProperty(indexed=False))
    vastaaja = field(d, 'vastaaja', ndb.StringProperty(indexed=False))
    vastaaja_id = field(d, 'vastaaja_id', ndb.StringProperty(indexed=False), internal=True)
    virallinen_lausunto_lonkka = field(d, 'virallinen_lausunto_lonkka', ndb.StringProperty(indexed=False))
    virallinen_lausunto_kyynar = field(d, 'virallinen_lausunto_kyynar', ndb.StringProperty(indexed=False))
    virallinen_lausunto_silma = field(d, 'virallinen_lausunto_silma', ndb.StringProperty(indexed=False))
    virallinen_lausunto_muut = field(d, 'virallinen_lausunto_muut', ndb.StringProperty(indexed=False))
    luusto_nivel_operoitu = field(d, 'luusto_nivel_operoitu', ndb.BooleanProperty(indexed=False))
    luusto_nivel_operoitu_lisaselvitys = field(d, 'luusto_nivel_operoitu_lisaselvitys', ndb.StringProperty(indexed=False))
    luusto_nivel_tutkittu = field(d, 'luusto_nivel_tutkittu', ndb.BooleanProperty(indexed=False))
    luusto_nivel_tutkittu_lisaselvitys = field(d, 'luusto_nivel_tutkittu_lisaselvitys', ndb.StringProperty(indexed=False))
    selkarankamuutokset = field(d, 'selkarankamuutokset', ndb.BooleanProperty(indexed=False))
    selkarankamuutokset_lisaselvitys = field(d, 'selkarankamuutokset_lisaselvitys', ndb.StringProperty(indexed=False))
    korvatulehdus = field(d, 'korvatulehdus', ndb.BooleanProperty(indexed=False))
    virtsatietulehdus = field(d, 'virtsatietulehdus', ndb.BooleanProperty(indexed=False))
    anaalirauhastulehdus = field(d, 'anaalirauhastulehdus', ndb.BooleanProperty(indexed=False))
    eturauhastulehdus = field(d, 'eturauhastulehdus', ndb.BooleanProperty(indexed=False))
    silmatulehdus = field(d, 'silmatulehdus', ndb.BooleanProperty(indexed=False))
    suolistotulehdus = field(d, 'suolistotulehdus', ndb.BooleanProperty(indexed=False))
    tulehtunut_rasvapatti = field(d, 'tulehtunut_rasvapatti', ndb.BooleanProperty(indexed=False))
    kohtutulehdus = field(d, 'kohtutulehdus', ndb.BooleanProperty(indexed=False))
    muu_tulehdus = field(d, 'muu_tulehdus', ndb.BooleanProperty(indexed=False))
    tulehdussairaudet_lisaselvitys = field(d, 'tulehdussairaudet_lisaselvitys', ndb.StringProperty(indexed=False))
    slo = field(d, 'slo', ndb.BooleanProperty(indexed=False))
    imha = field(d, 'imha', ndb.BooleanProperty(indexed=False))
    addison = field(d, 'addison', ndb.BooleanProperty(indexed=False))
    kilpirauhasen_vajaatoiminta = field(d, 'kilpirauhasen_vajaatoiminta', ndb.BooleanProperty(indexed=False))
    munuaisten_vajaatoiminta = field(d, 'munuaisten_vajaatoiminta', ndb.BooleanProperty(indexed=False))
    haiman_vajaatoiminta = field(d, 'haiman_vajaatoiminta', ndb.BooleanProperty(indexed=False))
    sle = field(d, 'sle', ndb.BooleanProperty(indexed=False))
    itp = field(d, 'itp', ndb.BooleanProperty(indexed=False))
    epilepsia = field(d, 'epilepsia', ndb.BooleanProperty(indexed=False))
    sydanvika = field(d, 'sydanvika', ndb.BooleanProperty(indexed=False))
    virtsakivet = field(d, 'virtsakivet', ndb.BooleanProperty(indexed=False))
    cushing = field(d, 'cushing', ndb.BooleanProperty(indexed=False))
    allergia = field(d, 'allergia', ndb.BooleanProperty(indexed=False))
    diabetes = field(d, 'diabetes', ndb.BooleanProperty(indexed=False))
    lihassurkastuma = field(d, 'lihassurkastuma', ndb.BooleanProperty(indexed=False))
    muut_sairaudet_lisaselvitys = field(d, 'muut_sairaudet_lisaselvitys', ndb.StringProperty(indexed=False))
    hyvanlaatuinen_kasvain = field(d, 'hyvanlaatuinen_kasvain', ndb.BooleanProperty(indexed=False))
    hyvanlaatuinen_kasvain_lisaselvitys = field(d, 'hyvanlaatuinen_kasvain_lisaselvitys', ndb.StringProperty(indexed=False))
    syopa = field(d, 'syopa', ndb.BooleanProperty(indexed=False))
    syopa_lisaselvitys = field(d, 'syopa_lisaselvitys', ndb.StringProperty(indexed=False))
    napatyra = field(d, 'napatyra', ndb.BooleanProperty(indexed=False))
    napatyra_leikattu = field(d, 'napatyra_leikattu', ndb.BooleanProperty(indexed=False))
    leikkaava_purenta = field(d, 'leikkaava_purenta', ndb.BooleanProperty(indexed=False))
    tasapurenta = field(d, 'tasapurenta', ndb.BooleanProperty(indexed=False))
    alapurenta = field(d, 'alapurenta', ndb.BooleanProperty(indexed=False))
    ylapurenta = field(d, 'ylapurenta', ndb.BooleanProperty(indexed=False))
    hammaspuutos_p1_p4 = field(d, 'hammaspuutos_p1_p4', ndb.BooleanProperty(indexed=False))
    hammaspuutos_etuhampaat = field(d, 'hammaspuutos_etuhampaat', ndb.BooleanProperty(indexed=False))
    hammaspuutos_poskihampaat = field(d, 'hammaspuutos_poskihampaat', ndb.BooleanProperty(indexed=False))
    liikahampaat = field(d, 'liikahampaat', ndb.BooleanProperty(indexed=False))
    hammaspuutos_liikahammas_lisaselvitys = field(d, 'hammaspuutos_liikahammas_lisaselvitys', ndb.StringProperty(indexed=False))
    kitalakeen_painuvat_kulmahampaat_pentuna = field(d, 'kitalakeen_painuvat_kulmahampaat_pentuna', ndb.BooleanProperty(indexed=False))
    kitalakeen_painuvat_kulmahampaat_aikuisena = field(d, 'kitalakeen_painuvat_kulmahampaat_aikuisena', ndb.BooleanProperty(indexed=False))
    kives_normaali = field(d, 'kives_normaali', ndb.BooleanProperty(indexed=False))
    kives_toispuoleinen_puutos = field(d, 'kives_toispuoleinen_puutos', ndb.BooleanProperty(indexed=False))
    kives_molemminpuolinen_puutos = field(d, 'kives_molemminpuolinen_puutos', ndb.BooleanProperty(indexed=False))
    kives_hissikives = field(d, 'kives_hissikives', ndb.BooleanProperty(indexed=False))
    kives_myohaan_laskeutunut = field(d, 'kives_myohaan_laskeutunut', ndb.BooleanProperty(indexed=False))
    uros_astuminen = field(d, 'uros_astuminen', ndb.BooleanProperty(indexed=False))
    uros_astuminen_helppo = field(d, 'uros_astuminen_helppo', ndb.BooleanProperty(indexed=False))
    uros_astuminen_ongelmia = field(d, 'uros_astuminen_ongelmia', ndb.BooleanProperty(indexed=False))
    uros_astuminen_lisaselvitys = field(d, 'uros_astuminen_lisaselvitys', ndb.StringProperty(indexed=False))
    uros_jalkelaisia = field(d, 'uros_jalkelaisia', ndb.BooleanProperty(indexed=False))
    uros_jalkelaisissa_sairauksia_vikoja = field(d, 'uros_jalkelaisissa_sairauksia_vikoja', ndb.BooleanProperty(indexed=False))
    uros_jalkelaiset_lisaselvitys = field(d, 'uros_jalkelaiset_lisaselvitys', ndb.StringProperty(indexed=False))
    narttu_valeraskauksia = field(d, 'narttu_valeraskauksia', ndb.BooleanProperty(indexed=False))
    narttu_saannollinen_kiima = field(d, 'narttu_saannollinen_kiima', ndb.BooleanProperty(indexed=False))
    narttu_kiimakierron_pituus = field(d, 'narttu_kiimakierron_pituus', ndb.StringProperty(indexed=False))
    narttu_kaytetty_jalostukseen = field(d, 'narttu_kaytetty_jalostukseen', ndb.BooleanProperty(indexed=False))
    narttu_ei_anna_astua = field(d, 'narttu_ei_anna_astua', ndb.BooleanProperty(indexed=False))
    narttu_jaanyt_tyhjaksi = field(d, 'narttu_jaanyt_tyhjaksi', ndb.BooleanProperty(indexed=False))
    narttu_raskaus_keskeytynyt = field(d, 'narttu_raskaus_keskeytynyt', ndb.BooleanProperty(indexed=False))
    narttu_ei_hoida_pentuja_hyvin = field(d, 'narttu_ei_hoida_pentuja_hyvin', ndb.BooleanProperty(indexed=False))
    narttu_jalostus_lisaselvitys = field(d, 'narttu_jalostus_lisaselvitys', ndb.StringProperty(indexed=False))
    paukkuarka = field(d, 'paukkuarka', ndb.BooleanProperty(indexed=False))
    aaniherkka = field(d, 'aaniherkka', ndb.BooleanProperty(indexed=False))
    stressaa_helposti = field(d, 'stressaa_helposti', ndb.BooleanProperty(indexed=False))
    aaniherkkyys_stressaus_lisaselvitys = field(d, 'aaniherkkyys_stressaus_lisaselvitys', ndb.StringProperty(indexed=False))
    muut_pelot = field(d, 'muut_pelot', ndb.BooleanProperty(indexed=False))
    muut_pelot_lisaselvitys = field(d, 'muut_pelot_lisaselvitys', ndb.StringProperty(indexed=False))
    luonnetesti_lisaselvitys = field(d, 'luonnetesti_lisaselvitys', ndb.StringProperty(indexed=False))
    muuta_huomioitavaa = field(d, 'muuta_huomioitavaa', ndb.StringProperty(indexed=False))
    email = field(d, 'email', ndb.StringProperty(indexed=False))

class Role (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    user_id = field(d, 'user_id', ndb.StringProperty())
    role = field(d, 'role', ndb.StringProperty())
    target = field(d, 'target', ndb.KeyProperty())

class Profile (ndb.Model, UriAddressable):
    d = dict(UriAddressable.d.items())
    user_id = field(d, 'user_id', ndb.StringProperty())
    nickname = field(d, 'nickname', ndb.StringProperty())

