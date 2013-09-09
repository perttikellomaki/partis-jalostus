import time
import logging
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

class KoiraAutocomplete(ndb.Model):
    virallinen_nimi = ndb.StringProperty()
    canonical = ndb.StringProperty()
    uros = ndb.BooleanProperty()

def field(d, name, prop, uri_prefix=None):
    d[name] = (prop, uri_prefix)
    return prop

class Modtime(ndb.Model):
    modtime = ndb.DateTimeProperty(auto_now=True)

    def hashify(self):
        return {'modtime': str(time.mktime(self.modtime.timetuple()))}

class SignedResource(polymodel.PolyModel):
    d = {}    # dictonary for collecting fields
    author =       field(d, 'author', ndb.StringProperty())
    author_nick =  field(d, 'author_nick', ndb.StringProperty())
    author_email = field(d, 'author_email', ndb.StringProperty())
    timestamp =    field(d, 'timestamp', ndb.DateTimeProperty(auto_now=True))

    # archive_copy_of is intentionally not defined using field()
    archive_copy_of = ndb.KeyProperty()

    def uri(self):
        return "/%s/%s" % (self.__class__.__name__, self.key.urlsafe())

    def fields(self):
        return self.__class__.d

    def hashify(self):
        res = {'uri': self.uri()}
        for name, info in self.fields().items():
            field, uri_prefix = info
            val = field.__get__(self, type(self))
            if val:
                if isinstance(field, ndb.StringProperty):
                    res[name] = val
                elif isinstance(field, ndb.KeyProperty):
                    res[name] = "%s/%s" % (uri_prefix, val.urlsafe())
                elif isinstance(field, ndb.DateTimeProperty):
                    res[name] = val.isoformat()
                else:
                    res[name] = str(val)

        modtime = ndb.Key('Modtime', 'modtime', parent=self.key).get()
        if modtime:
            res['modtime'] = str(time.mktime(modtime.modtime.timetuple()))

        return res
            

    def populateFromRequest(self, params):
        for name, info in self.fields().items():
            field, _ = info
            if params.has_key(name) and params[name] != 'undefined':
                if isinstance(field, ndb.StringProperty):
                    field.__set__(self, params[name])
                elif isinstance(field, ndb.BooleanProperty):
                    field.__set__(self, params[name] == 'true')
                elif isinstance(field, ndb.IntegerProperty):
                    try:
                        field.__set__(self, int(params[name]))
                    except:
                        pass
                elif isinstance(field, ndb.DateProperty):
                    try:
                        field.__set__(self, dateutil.parser.parse(params[name]))
                    except:
                        pass
                elif isinstance(field, ndb.KeyProperty):
                    try:
                        key = params[name].split("/")[2]
                        field.__set__(self, ndb.Key(urlsafe=key))
                    except:
                        pass
                        
                    
    def subsumes(self, item):
        """Return true if self is signed by the same user, and
        the information contained in self is a superset of the
        information in item."""

        for name, info in self.fields().items():
            if name != 'timestamp':
                field, uri_prefix = info
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

    def sign(self, user):
        self.author = str(user.user_id())
        self.author_nick = user.nickname()
        self.author_email = user.email()

    def archive_fields(self, copy):
        for name, info in self.fields().items():
            field, _ = info
            field.__set__(copy, field.__get__(self, type(self)))
        copy.archive_copy_of = self.key
        return copy

    def Put(self):
        """Put to datastore and stamp modtime."""
        self.put()
        modtimeKey = ndb.Key('Modtime', 'modtime', parent=self.key)
        modtimeEntity = modtimeKey.get()
        if modtimeEntity is None:
            modtimeEntity = Modtime(id="modtime", parent=self.key)
        modtimeEntity.put()

    individual_handler_ = None
    collection_handler_ = None

    @classmethod
    def individualHandler(cls, handler=None):
        if handler:
            cls.individual_handler_ = handler
        return cls.individual_handler_

    @classmethod
    def collectionHandler(cls, handler=None):
        if handler:
            cls.collection_handler_ = handler
        return cls.collection_handler_

    @classmethod
    def UriPrefix(cls):
        return "/%s" % cls.__name__
    
    def uriPrefix(self):
        return self.__class__.UriPrefix()

    def uri(self):
        return "%s/%s" % (self.uriPrefix(), self.key.urlsafe())


class Koira(SignedResource):
    d = dict(SignedResource.d.items())
    virallinen_nimi = field(d, 'virallinen_nimi', ndb.StringProperty())
    kutsumanimi =     field(d, 'kutsumanimi', ndb.StringProperty())
    kennel =          field(d, 'kennel', ndb.StringProperty())
    sukupuoli =       field(d, 'sukupuoli', ndb.StringProperty())
    syntymapaiva =    field(d, 'syntymapaiva', ndb.DateProperty())
    syntymavuosi =    field(d, 'syntymavuosi', ndb.IntegerProperty())
    isa =             field(d, 'isa', ndb.KeyProperty(), uri_prefix="/Koira")
    ema =             field(d, 'ema', ndb.KeyProperty(), uri_prefix="/Koira")

    def archive(self):
        """Create archival copy"""
        copy = Koira()
        return self.archive_fields(copy)

class Terveyskysely(SignedResource):
    d = dict(SignedResource.d.items())
    virallinen_nimi    = field(d, 'virallinen_nimi', ndb.StringProperty())
    autoimmuunisairaus = field(d, 'autoimmuunisairaus', ndb.BooleanProperty())
    slo                = field(d, 'slo', ndb.BooleanProperty())
    imha               = field(d, 'imha', ndb.BooleanProperty())

class YhdistysPaimennustaipumus(SignedResource):
    d = dict(SignedResource.d.items())
    koira =              field(d, 'koira', ndb.KeyProperty(), uri_prefix="/Koira")
    kiinnostus =         field(d, 'kiinnostus', ndb.IntegerProperty())
    taipumus =           field(d, 'taipumus', ndb.IntegerProperty())
    henkinen_kestavyys = field(d, 'henkinen_kestavyys',  ndb.IntegerProperty())
    ohjattavuus =        field(d, 'ohjattavuus', ndb.IntegerProperty())
    tuomari =            field(d, 'tuomari', ndb.StringProperty())
    paikka =             field(d, 'paikka', ndb.StringProperty())
    paiva =              field(d, 'paiva', ndb.DateProperty())

    def archive(self):
        """Create archival copy"""
        copy = YhdistysPaimennustaipumus()
        return self.archive_fields(copy)

