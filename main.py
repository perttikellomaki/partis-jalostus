#!/usr/bin/env python
#
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import json
import os
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
        if not base:
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
        logging.info("KoiraHandler")
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
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
                  <html><head><title>Login</title></head><body>
                  <a href="%s">Login</a>
                  </body> </html>"""
                % users.create_login_url("/"))

class HistoryHandler(HardenedHandler):
    def get_(self, user, key):
        resources = SignedResource.gql("WHERE archive_copy_of = KEY(:1)",
                                       key)
        data = []
        for res in resources:
            data.append(res.hashify())
        self.jsonReply(data)

app = webapp2.WSGIApplication(
    [("/Koira", KoiraCollectionHandler),
     ("/Koira/([^/]+)", KoiraHandler),
     ("/History/([^/]+)", HistoryHandler),
     ("/Login", LoginHandler),
     ],
    debug=True)
