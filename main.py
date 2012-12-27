#!/usr/bin/env python
#
import webapp2
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import json
import os
import logging

whitelist = ["114665306391201355583"    #pertti.kellomaki@gmail.com
             ]
PRODUCTION = not os.environ['SERVER_SOFTWARE'].startswith('Development')

class HardenedHandler(webapp2.RequestHandler):
    """Factors out common preconditions for get() and post() methods."""

    def get(self, *args, **kwargs):
        if PRODUCTION and (users.get_current_user().user_id() not in whitelist):
            pass
        else:
            self.get_(*args, **kwargs)

    def post(self, *args, **kwargs):
        if PRODUCTION and (users.get_current_user().user_id() not in whitelist):
            pass
        else:
            self.post_(*args, **kwargs)

    def jsonReply(self, data):
        logging.info("jsonReply => %s" % data)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.dumps(data))

class SignedResource(polymodel.PolyModel):
    user = db.StringProperty()
    timestamp = db.DateTimeProperty(auto_now=True)

    def hashify(self, base=None):
        if not base:
            base = {}
        base['user'] = self.user
        base['timestamp'] = str(self.timestamp)
        return base

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

class KoiraCollectionHandler(HardenedHandler):
    def get_(self):
        dogs = Koira.all()
        data = []
        for d in dogs:
            logging.info("FOO " + str(d))
            logging.info(str(d.hashify()))
            data.append(d.hashify())
            logging.info("DATA: " + str(data))
        self.jsonReply(data)

    def post_(self):
        dog = Koira(virallinen_nimi = self.request.params['virallinen_nimi'])
        dog.put()
        self.jsonReply(dog.hashify())

class KoiraHandler(HardenedHandler):
    def get_(self, key):
        logging.info("KoiraHandler")
        dog = db.get(key)
        self.jsonReply(dog.hashify())

class LoginHandler(HardenedHandler):
    def get_(self, user):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
                  <html><head><title>Login</title></head><body>
                  <a href="%s">Login</a>
                  </body> </html>"""
                % users.create_login_url("/"))
  

app = webapp2.WSGIApplication(
    [("/Koira", KoiraCollectionHandler),
     ("/Koira/([^/]+)", KoiraHandler),
     ("/Login", LoginHandler),
     ],
    debug=True)
