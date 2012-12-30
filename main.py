#!/usr/bin/env python
#
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import json
import os
import datetime
import logging
from HardenedHandler import HardenedHandler

whitelist = ["114665306391201355583"    #pertti.kellomaki@gmail.com
             ]
PRODUCTION = not os.environ['SERVER_SOFTWARE'].startswith('Development')

class SignedResource(polymodel.PolyModel):
    author = db.StringProperty()
    author_nick = db.StringProperty()
    author_email = db.EmailProperty()
    timestamp = db.DateTimeProperty(auto_now=True)
    archive_copy_of = db.ReferenceProperty()

    def sign(self, user):
        self.author = user.user_id()
        self.author_nick = user.nickname()
        self.author_email = user.email()

    def hashify(self, base=None):
        if base is None:
            base = {}
        base['author_nick'] = self.author_nick
        base['timestamp'] = str(self.timestamp)
        return base

    def archive_fields(self, copy):
        copy.author = self.author
        copy.author_nick = self.author_nick
        copy.author_email = self.author_email
        copy.timestamp = self.timestamp
        copy.archive_copy_of = self.key()

class Koira(SignedResource):
    virallinen_nimi = db.StringProperty()
    
    def uri(self):
        return "/Koira/%s" % str(self.key())

    def hashify(self, base=None):
        if base is None:
            base = {}
        super(Koira, self).hashify(base=base)
        base['uri'] = self.uri()
        base['virallinen_nimi'] = self.virallinen_nimi
        return base

    def archive_fields(self, copy):
        copy.virallinen_nimi = self.virallinen_nimi
        super(Koira, self).archive_fields(copy)

    def archive(self):
        """Create archival copy"""
        copy = Koira()
        self.archive_fields(copy)
        return copy

class Paimennustaipumus(SignedResource):
    koira = db.ReferenceProperty()
    kiinnostus = db.IntegerProperty()
    taipumus = db.IntegerProperty()
    henkinen_kestavyys =  db.IntegerProperty()
    ohjattavuus = db.IntegerProperty()
    tuomari = db.StringProperty()
    paikka = db.StringProperty()
    paiva = db.DateProperty()

    def uri(self):
        return "/Paimennustaipumus/%s" % str(self.key())

    def hashify(self, base=None):
        if base is None:
            base = {}
        super(Paimennustaipumus, self).hashify(base=base)
        base['koira'] = self.koira.uri()
        base['uri'] = self.uri()
        base['kiinnostus'] = self.kiinnostus
        base['taipumus'] = self.taipumus
        base['henkinen_kestavyys'] = self.henkinen_kestavyys
        base['ohjattavuus'] = self.ohjattavuus
        base['tuomari'] = self.tuomari
        base['paikka'] = self.paikka
        base['paiva'] = self.paiva.strftime("%d.%m.%Y")
        return base

    def archive_fields(self, copy):
        copy.koira = self.koira
        copy.kiinnostus = self.kiinnostus
        copy.taipumus = self.taipumus
        copy.henkinen_kestavyys = self.henkinen_kestavyys
        copy.ohjattavuus = self.ohjattavuus
        copy.tuomari = self.tuomari
        copy.paikka = self.paikka
        copy.paiva = self.paiva
        super(Paimennustaipumus, self).archive_fields(copy)

    def archive(self):
        """Create archival copy"""
        copy = Paimennustaipumus()
        self.archive_fields(copy)
        return copy

class KoiraCollectionHandler(HardenedHandler):
    def get_(self, user):
        dogs = Koira.all()
        data = []
        for d in dogs:
            if d.archive_copy_of == None:
                data.append(d.hashify())
        self.jsonReply(data)

    def post_(self, user):
        dog = Koira(virallinen_nimi = self.request.params['virallinen_nimi'])
        dog.sign(user)
        dog.put()
        self.jsonReply(dog.hashify())

class KoiraHandler(HardenedHandler):
    def get_(self, user, key):
        dog = db.get(key)
        self.jsonReply(dog.hashify())

    def post_(self, user, key):
        dog = db.get(key)
        dog.virallinen_nimi = self.request.params['virallinen_nimi']
        dog.sign(user)
        dog.put()
        self.jsonReply(dog.hashify())

class LoginHandler(HardenedHandler):
    def get_(self, user):

        providers = {
            'Google'   : 'https://www.google.com/accounts/o8/id',
            'Yahoo'    : 'yahoo.com',
            'MySpace'  : 'myspace.com'}

        logging.info("provides.items() => %s" % (providers.items(),))

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
                  <html><head><title>Login</title></head><body>
                  Kirjaudu sisään jollain seuraavista tunnuksista:<br>""")
        for name, uri in providers.items():
            self.response.out.write('[<a href="%s">%s</a>]'
                                    % (users.create_login_url(federated_identity=uri),
                                       name))
        self.response.out.write("""</body> </html>""")

class HistoryHandler(HardenedHandler):
    def get_(self, user, key):
        resources = SignedResource.gql("WHERE archive_copy_of = KEY(:1)",
                                       key)
        data = []
        for res in resources:
            data.append(res.hashify())
        self.jsonReply(data)

class PaimennustaipumusCollectionHandler(HardenedHandler):
    def get_(self, user):
        tests = Paimennustaipumus.gql("WHERE koira = KEY(:1)",
                                      self.request.params['koira'])
        data = []
        for t in tests:
            data.append(t.hashify())
        self.jsonReply(data)

    def post_(self, user):
        koira = db.get(self.request.params['koira'])
        day, month, year = self.request.params['paiva'].split(".")
        paiva = datetime.date(int(year), int(month), int(day))
        test = Paimennustaipumus(
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

class PaimennustaipumusHandler(HardenedHandler):
    def post_(self, user, key):
        test = db.get(key)
        day, month, year = self.request.params['paiva'].split(".")
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

app = webapp2.WSGIApplication(
    [("/Koira", KoiraCollectionHandler),
     ("/Koira/([^/]+)", KoiraHandler),
     ("/History/([^/]+)", HistoryHandler),
     ("/Paimennustaipumus", PaimennustaipumusCollectionHandler),
     ("/Paimennustaipumus/([^/]+)", PaimennustaipumusHandler),
     ("/Login", LoginHandler),
     ("/LoginStatus", LoginStatusHandler),
     ],
    debug=True)
