#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
import uuid
import webapp2
from webapp2_extras import sessions
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
import json
import os
import datetime
import time
import dateutil
import dateutil.parser
import logging
from HardenedHandler import HardenedHandler, LocalUser

def field(d, name, prop, uri_prefix=None):
    d[name] = (prop, uri_prefix)
    return prop

class ModTime(ndb.Model):
    modtime = ndb.DateTimeProperty(auto_now=True)
    parent_uri = ndb.StringProperty()

    def hashify(self):
        if self.parent_uri is None:
            self.parent_uri = self.key.parent().get().uri()
        return {'modtime': str(time.mktime(self.modtime.timetuple())),
                'uri': self.parent_uri}

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

        modtime = ndb.Key('ModTime', 'modtime', parent=self.key).get()
        if modtime:
            res['modtime'] = str(time.mktime(modtime.modtime.timetuple()))

        return res
            

    def populateFromRequest(self, params):
        for name, info in self.fields().items():
            field, _ = info
            if params.has_key(name) and params[name] != 'undefined':
                if isinstance(field, ndb.StringProperty):
                    field.__set__(self, params[name])
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

class KoiraCollectionHandler(HardenedHandler):
    def get_(self, user):
        if (self.request.params.has_key('sukupuoli')
            and self.request.params['sukupuoli'] != ''
            and self.request.params['sukupuoli'] != 'undefined'):
            query = ndb.gql("SELECT * FROM Koira WHERE archive_copy_of = NULL AND sukupuoli = :1 ORDER BY virallinen_nimi ASC",
                            self.request.params['sukupuoli'])
        else:
            query = ndb.gql("SELECT * FROM Koira WHERE archive_copy_of = NULL ORDER BY virallinen_nimi ASC")

        self.genericGetCollection(query)

    def post_(self, user):
        dog = Koira()
        dog.populateFromRequest(self.request.params)
        dog.sign(user)
        dog.put()

        modtime = ModTime(id="modtime", parent=dog.key)
        modtime.put()
        self.jsonReply(dog.hashify())

class KoiraHandler(HardenedHandler):
    def get_(self, user, urlsafe):
        key = self.lookupKey(urlsafe=urlsafe)
        logging.info("key: %s" % key)
        if self.request.params.has_key('modtime'):
            entry_key = ndb.Key('ModTime', 'modtime', parent=key)
            logging.info("entry_key: %s" % entry_key)
            entry = entry_key.get()
            self.jsonReply(entry.hashify())
        else:
            dog = key.get()
            self.jsonReply(dog.hashify())

    def post_(self, user, key):
        dog = ndb.Key(urlsafe=key).get()
        dog.populateFromRequest(self.request.params)
        dog.sign(user)
        dog.put()
        self.jsonReply(dog.hashify())

class FederatedLoginHandler(HardenedHandler):
    def get_(self, user):

        providers = {
            'Google'   : 'https://www.google.com/accounts/o8/id',
            'Yahoo'    : 'yahoo.com',
            'MySpace'  : 'myspace.com'}

        data = []
        for name, uri in providers.items():
            data.append(
                {'name': name,
                 'uri': users.create_login_url(federated_identity=uri)})
        self.jsonReply(data)

class LocalLoginHandler(HardenedHandler):
    def post_unauthenticated_(self):
        entries = LocalUser.gql("WHERE email = :1 and password = :2",
                                self.request.params['email'],
                                self.request.params['password'])
        if entries.count() == 1:
            self.jsonReply({'email': '',
                            'password': '',
                            'status_message': 'Kirjautuminen onnistui'})
            user = entries.get()

            # record user data in session
            self.session['email'] = user.email
            self.session['user_id'] = "local-%s" % user.key().id()
            self.session['nickname'] = user.nickname
        else:
            self.jsonReply({'email': '',
                            'password': '',
                            'status_message': 'Kirjautuminen ei onnistunut'})
            

class LogoutHandler(HardenedHandler):
    def get_(self, user):
        # clear possible user information from session
        self.session['email'] = ''
        self.session['user_id'] = ''
        self.session['nickname'] = ''

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
                  <html><head><title>Logout</title></head>
                  <body><a href="%s">Logout</a></body></html>"""
                                % users.create_logout_url("/"))

class HistoryHandler(HardenedHandler):
    def get_(self, user, key):
        self.genericGetCollection(
            SignedResource.gql("WHERE archive_copy_of = KEY(:1) ORDER BY timestamp DESC",
                               key))

class YhdistysPaimennustaipumusCollectionHandler(HardenedHandler):
    def get_(self, user):
        koira = self.lookupKey(param='koira')
        self.genericGetCollection(
            YhdistysPaimennustaipumus.gql("WHERE koira = :1 AND archive_copy_of = NULL",
                                  koira))

    def post_(self, user):
        koira = self.lookupKey(param='koira')
        year, month, day = self.request.params['paiva'].split("-")
        paiva = datetime.date(int(year), int(month), int(day))
        test = YhdistysPaimennustaipumus(
            koira = koira,
            kiinnostus = int(self.request.params['kiinnostus']),
            taipumus = int(self.request.params['taipumus']),
            henkinen_kestavyys = int(self.request.params['henkinen_kestavyys']),
            ohjattavuus = int(self.request.params['ohjattavuus']),
            tuomari = self.request.params['tuomari'],
            paikka = self.request.params['paikka'],
            paiva = paiva)
        test.sign(user)
        test.put()
        self.jsonReply(test.hashify())

class YhdistysPaimennustaipumusHandler(HardenedHandler):
    def post_(self, user, key):
        test = self.lookupKey(urlsafe=key).get()
        year, month, day = self.request.params['paiva'].split("-")
        paiva = datetime.date(int(year), int(month), int(day))
        test.kiinnostus = int(self.request.params['kiinnostus'])
        test.taipumus = int(self.request.params['taipumus'])
        test.henkinen_kestavyys = int(self.request.params['henkinen_kestavyys'])
        test.ohjattavuus = int(self.request.params['ohjattavuus'])
        test.tuomari = self.request.params['tuomari']
        test.paikka = self.request.params['paikka']
        test.paiva = paiva
        test.sign(user)
        test.put()
        self.jsonReply(test.hashify())

class LoginStatusHandler(HardenedHandler):
    def get_(self, user):
        if user:
            self.jsonReply({
                    'logged_in': True,
                    'nick': user.nickname(),
                    'email': str(user.email())})
        else:
            self.jsonReply({
                    'logged_in': False,
                    'nick': None,
                    'email': None})

class PasswordRequestHandler(HardenedHandler):
    def post_unauthenticated_(self):
        if self.request.params['secret'] == "Suomen Partacolliet ry.":
            email = self.request.params['email']
            entries = LocalUser.gql("WHERE email = :1", email)
            if entries.count() == 0:
                entry = LocalUser(email = email,
                                  nickname = self.request.params['nickname'],
                                  password = uuid.uuid4().hex)
                entry.put()
            else:
                entry = entries.get()
            message = mail.EmailMessage()
            #message.sender = "noreply@%s.appspot.com" % app_identity.get_application_id()
            message.sender = "pertti.kellomaki@gmail.com"
            message.to = email
            message.subject = "Uusi salasana"
            message.body = ("""Hei!

Pyysit salasanaa Suomen Partacolliet ry:n jalostustietokantaan. 
Voit kirjautua osoitteellasi %s ja salasanalla %s
""" % (entry.email, entry.password))
            message.send()
            self.jsonReply({'email': '', 'nick': '', 'secret': '',
                            'status_message': 'Viesti matkalla'})

class CompactHistoryHandler(webapp2.RequestHandler):
    def post(self, key):
        history = SignedResource.gql("WHERE archive_copy_of = KEY(:1) ORDER BY timestamp DESC",
                                     key)
        top = ndb.Key(urlsafe=key).get()
        to_delete = []
        for item in history:
            if top.subsumes(item):
                to_delete.append(item.key)
            else:
                # only compact top of history
                break
        logging.info("CompactHistory : delete %s" % to_delete)
        ndb.delete_multi(to_delete)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'topsecretkey',
    }

app = webapp2.WSGIApplication(
    [("/Koira", KoiraCollectionHandler),
     ("/Koira/([^/]+)", KoiraHandler),
     ("/History/([^/]+)", HistoryHandler),
     ("/YhdistysPaimennustaipumus", YhdistysPaimennustaipumusCollectionHandler),
     ("/YhdistysPaimennustaipumus/([^/]+)", YhdistysPaimennustaipumusHandler),
     ("/FederatedLogin", FederatedLoginHandler),
     ("/LocalLogin", LocalLoginHandler),
     ("/Logout", LogoutHandler), 
     ("/LoginStatus", LoginStatusHandler),
     ("/PasswordRequest", PasswordRequestHandler),
     ("/CompactHistory/([^/]+)", CompactHistoryHandler),
     ],
    config=config,
    debug=True)
