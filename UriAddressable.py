import time
import dateutil
import dateutil.tz
import dateutil.parser
import logging

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class ModTime(ndb.Model):
    """Modification time of an entity."""
    modtime = ndb.DateTimeProperty(auto_now=True)
    parent_uri = ndb.StringProperty()

    def hashify(self):
        if self.parent_uri is None:
            self.parent_uri = self.key.parent().get().uri()
        return {'modtime': str(time.mktime(self.modtime.timetuple())),
                'uri': self.parent_uri}

class DependentModTime(ndb.Model):
    """Last modification time of a dependent entity (child node, comment, ...)."""
    modtime = ndb.DateTimeProperty(auto_now=True)

    def hashify(self):
        return {'depmodtime': str(time.mktime(self.modtime.timetuple()))}


def field(d, name, prop, 
          uri_prefix=None, populate_from_owner=False, internal=False, 
          only_admin_can_change=False, readonly=False, force_ssl=False,
          read_restrict_for_roles=None):
    d[name] = (prop, uri_prefix, populate_from_owner, internal, only_admin_can_change, readonly, force_ssl, read_restrict_for_roles)
    return prop

class UriAddressable(object):
    d = {}    # dictonary for collecting fields
    timestamp =    field(d, 'timestamp', ndb.DateTimeProperty(auto_now=True))

    def useModTime(self):
        """Overridden in subclasses to tell whether to attach a ModTime entity to self."""
        return False

    def fields(self):
        return self.__class__.d

    def hashify(self, user_id=None):
        res = {'uri': self.uri()}
        if isinstance(self, polymodel.PolyModel):
            res['class'] = self.__class__.__name__
        for name, info in self.fields().items():
            field, uri_prefix, _, internal, _, _, force_ssl, read_restrict_for_roles = info
            if read_restrict_for_roles:
                show = False
                if user_id is not None:
                    for role in ndb.gql("SELECT * FROM Role WHERE user_id=:1 AND valid=true", user_id):
                        if role.role in read_restrict_for_roles:
                            show = True
                            break
            else:
                show = True

            if show and not internal:
                val = field.__get__(self, type(self))
                if val is not None:
                    if isinstance(field, ndb.StringProperty) and force_ssl:
                        # serve with ssl to avoid security complaints in browser
                        if val[0:len('http:')] == 'http:':
                            res[name] = val.replace('http:', 'https:')
                    elif (isinstance(field, ndb.StringProperty)
                        or isinstance(field, ndb.TextProperty)
                        or isinstance(field, ndb.BooleanProperty)):
                        res[name] = val
                    elif isinstance(field, ndb.IntegerProperty):
                        res[name] = str(val)
                    elif isinstance(field, ndb.KeyProperty):
                        if uri_prefix:
                            res[name] = "%s/%s" % (uri_prefix, val.urlsafe())
                        else:
                            res[name] = "/%s/%s" % (val.kind(), val.urlsafe())
                    elif isinstance(field, ndb.DateTimeProperty):
                        res[name] = "%sZ" % val.isoformat()
                    else:
                        res[name] = str(val)

        if self.useModTime():
            try:
                modtime = ndb.Key('ModTime', 'modtime', parent=self.key).get()
                res['modtime'] = str(time.mktime(modtime.modtime.timetuple()))
            except:
                logging.warning("Error getting modtime for %s", self)

        return res

    def populateFromRequest(self, params):
        for name, info in self.fields().items():
            field, _, populate_from_owner, internal, only_admin_can_change, readonly, _, _ = info
            if readonly or isinstance(field, ndb.ComputedProperty):
                pass
            elif only_admin_can_change and not users.is_current_user_admin():
                pass
            elif populate_from_owner:
                field.__set__(self, self.owner)
            elif internal:
                pass
            elif params.has_key(name) and params[name] != 'undefined':
                if (isinstance(field, ndb.StringProperty)
                    or isinstance(field, ndb.TextProperty)):
                    field.__set__(self, params[name])
                elif isinstance(field, ndb.IntegerProperty):
                    try:
                        field.__set__(self, int(params[name]))
                    except:
                        pass
                elif isinstance(field, ndb.BooleanProperty):
                    if params[name] == 'true' or params[name] is True:
                        field.__set__(self, True)
                    elif params[name] == 'false' or params[name] is False:
                        field.__set__(self, False)
                    else:
                        logging.error("Bad value for boolean field: %s" % params[name])
                        raise "Bad value for boolean field: %s" % params[name]
                elif isinstance(field, ndb.DateProperty):
                    try:
                        field.__set__(self, dateutil.parser.parse(params[name]))
                    except:
                        pass
                elif isinstance(field, ndb.DateTimeProperty):
                    datetime = dateutil.parser.parse(params[name])
                    field.__set__(self, datetime.astimezone(dateutil.tz.tzutc()).replace(tzinfo=None))
                elif isinstance(field, ndb.KeyProperty):
                    if params[name] == '':
                        field.__set__(self, None)
                    else:
                        try:
                            key = params[name].split("/")[2]
                            field.__set__(self, ndb.Key(urlsafe=key))
                        except:
                            pass
                else:
                    logging.info("field %s %s" % (name, type(field)))
                    raise "Unknown field type"

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
        if self.key is None:
            return None
        else:
            return "%s/%s" % (self.uriPrefix(), self.key.urlsafe())

    def Put(self):
        """Do .put() and stamp modtime if required."""
        self.put()
        if self.useModTime():
            self.stampModTime()

    def stampModTime(self):
        modtimeKey = ndb.Key('ModTime', 'modtime', parent=self.key)
        modtime = modtimeKey.get()
        if modtime:
            modtime.put()
        else:
            modtime = ModTime(id="modtime", parent=self.key)
            modtime.put()

    def stampDependentModTime(self):
        modtimeKey = ndb.Key('DependentModTime', 'dependent_modtime', parent=self.key)
        modtime = modtimeKey.get()
        if modtime:
            modtime.put()
        else:
            modtime = DependentModTime(id="dependent_modtime", parent=self.key)
            modtime.put()
