#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
import uuid
import webapp2
from webapp2_extras import sessions
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import json
import os
import datetime
import logging
from HardenedHandler import HardenedHandler, LocalUser

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

class LogoutHandler(HardenedHandler):
    def get_(self, user):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
                  <html><head><title>Logout</title></head>
                  <body><a href="%s">Logout</a></body></html>"""
                                % users.create_logout_url("/"))

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
        tests = Paimennustaipumus.gql("WHERE koira = KEY(:1) AND archive_copy_of = NULL",
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

class PasswordRequestHandler(HardenedHandler):
    def post_unauthenticated_(self):
        if self.request.params['secret'] == "Suomen Partacolliet ry.":
            email = self.request.params['email']
            entries = LocalUser.gql("WHERE email_ = :1", email)
            if entries.count() == 0:
                entry = LocalUser(userid_ = "userid",
                                  email_ = email,
                                  nick_ = self.request.params['nick'],
                                  password_ = uuid.uuid4().hex)
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
""" % (entry.email_, entry.password_))
            message.send()
            self.jsonReply({'email': '', 'nick': '', 'secret': '',
                            'status_message': 'Viesti matkalla'})
        

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'topsecretkey',
    }

app = webapp2.WSGIApplication(
    [("/Koira", KoiraCollectionHandler),
     ("/Koira/([^/]+)", KoiraHandler),
     ("/History/([^/]+)", HistoryHandler),
     ("/Paimennustaipumus", PaimennustaipumusCollectionHandler),
     ("/Paimennustaipumus/([^/]+)", PaimennustaipumusHandler),
     ("/FederatedLogin", FederatedLoginHandler),
     ("/Logout", LogoutHandler), 
     ("/LoginStatus", LoginStatusHandler),
     ("/PasswordRequest", PasswordRequestHandler)
     ],
    config=config,
    debug=True)
