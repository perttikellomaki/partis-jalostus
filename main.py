#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#%%import uuid
import webapp2
#%%from webapp2_extras import sessions
#%%from google.appengine.api import app_identity
#%%from google.appengine.api import mail
#%%from google.appengine.api import users
from google.appengine.ext import ndb
#%%from google.appengine.ext.ndb import polymodel
#%%import json
#%%import os
#%%import datetime
#%%import time
#%%import dateutil
#%%import dateutil.parser
import logging
from HardenedHandler import HardenedHandler, LocalUser
import DatastoreClasses
import Paimennustaipumus
import Terveyskysely
import Koira

class KoiraAutocomplete(ndb.Model):
    virallinen_nimi = ndb.StringProperty()
    canonical = ndb.StringProperty()
    uros = ndb.BooleanProperty()

class ModtimeHandler (HardenedHandler):

    def get_(self, key, user):
        parent = ndb.Key(urlsafe=key)
        modtime = ndb.Key('Modtime', 'modtime', parent=parent).get()
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.dumps(modtime.hashify()))

class KoiraAutoCompleteHandler(HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('sukupuoli'):
            query = ndb.gql("SELECT * FROM KoiraAutocomplete "
                            "WHERE uros = :1 AND canonical >= :2",
                            self.request.params['sukupuoli'] == 'uros',
                            self.request.params['prefix'].lower())
        else:
            query = ndb.gql("SELECT * FROM KoiraAutocomplete WHERE canonical >= :1",
                            self.request.params['prefix'].lower())
        maxlen = 5
        data = []
        for entity in query:
            if entity.canonical.startswith(self.request.params['prefix'].lower()):
                data.append(entity.virallinen_nimi)
            else:
                break
            if len(data) == maxlen:
                break
        self.jsonReply(data)

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
            DatastoreClasses.SignedResource.gql(
                "WHERE archive_copy_of = KEY(:1) ORDER BY timestamp DESC",
                key))

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
        history = DatastoreClasses.SignedResource.gql(
            "WHERE archive_copy_of = KEY(:1) ORDER BY timestamp DESC",
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

def handlers(classes):

    def individual(cls):
        return ("%s/([^/]+)" % cls.UriPrefix(),
                cls.individualHandler())

    def collection(cls):
        return (cls.UriPrefix(),
                cls.collectionHandler())

    res = []
    for cls in classes:
        if cls.individualHandler():
            res.append(individual(cls))
        if cls.collectionHandler():
            res.append(collection(cls))
    return res

handler_list = (
    handlers(
        [DatastoreClasses.Koira,
         DatastoreClasses.Terveyskysely,
         DatastoreClasses.YhdistysPaimennustaipumus])
    + [("/Modtime/([^/]+)", ModtimeHandler),
       ("/KoiraAutoComplete", KoiraAutoCompleteHandler),
       ("/History/([^/]+)", HistoryHandler),
       ("/FederatedLogin", FederatedLoginHandler),
       ("/LocalLogin", LocalLoginHandler),
       ("/Logout", LogoutHandler), 
       ("/LoginStatus", LoginStatusHandler),
       ("/PasswordRequest", PasswordRequestHandler),
       ("/CompactHistory/([^/]+)", CompactHistoryHandler),
       ])

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'topsecretkey',
    }

app = webapp2.WSGIApplication(
    handler_list,
    config=config,
    debug=True)
