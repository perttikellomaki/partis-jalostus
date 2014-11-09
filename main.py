#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
import uuid
import webapp2
import urllib
from webapp2_extras import sessions
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
import json
import logging
from HardenedHandler import HardenedHandler, LocalUser
import DatastoreClasses
import Paimennustaipumus
import Terveyskysely
import Koira
import Kennel
import Util
import Survey
import SurveySubmission

class ModTimeHandler (HardenedHandler):
    def get_(self, user, key):
        modtime_key = ndb.Key('ModTime', 'modtime', 
                              parent = ndb.Key(urlsafe=key))
        try:
            self.jsonReply(modtime_key.get().hashify(),
                           "ModTime => %s")
        except:
            parent = ndb.Key(urlsafe=key).get()
            if parent:
                parent.stampModTime()
                self.jsonReply(modtime_key.get().hashify())
            else:
                self.response.set_status(410)
                self.response.out.write("No such entity, maybe it has been deleted?")


class DepModTimeHandler (HardenedHandler):
    def get_(self, user, key):
        modtime_key = ndb.Key('DependentModTime', 'dependent_modtime', 
                              parent = ndb.Key(urlsafe=key))
        try:
            self.jsonReply(modtime_key.get().hashify(),
                           "DepModTime => %s")
        except:
            parent = ndb.Key(urlsafe=key).get()
            if parent:
                parent.stampDependentModTime()
                self.jsonReply(modtime_key.get().hashify())
            else:
                self.response.set_status(410)
                self.response.out.write("No such entity, maybe it has been deleted?")

class KoiraAutoCompleteHandler(HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('sukupuoli'):
            query = ndb.gql("SELECT * FROM KoiraAutocomplete "
                            "WHERE uros = :1 AND canonical >= :2",
                            self.request.params['sukupuoli'] == 'uros',
                            Util.canonical(self.request.params['prefix']))
        else:
            query = ndb.gql("SELECT * FROM KoiraAutocomplete WHERE canonical >= :1",
                            Util.canonical(self.request.params['prefix']))
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

class LocalLoginRedirectHandler(HardenedHandler):
    def get_(self, user):
        self.get_unauthenticated_()

    def get_unauthenticated_(self):
        entries = LocalUser.gql("WHERE email = :1",
                                self.request.params['email'])
        if entries.count() == 1:
            local_user = entries.get()

            if self.request.params['password'] == local_user.password:

                # record user data in session
                self.session['email'] = local_user.email
                self.session['user_id'] = "local:%s" % local_user.key.id()
                self.session['nickname'] = local_user.nickname
                
                self.redirect(str(self.request.params['redirect_url']))

            else:
                self.response.out.write("""<html><head><title>Salasanasi on vanhentunut</title></head>
<body><h1>Salasanasi on vanhentunut</h1><p>Ole hyvä ja tilaa uusi salasana sähköpostiisi.</p></body></html>""")
        else:
            self.response.out.write("""<html><head><title>Käyttäjää ei löydy</title></head><body><p>Tällä sähköpostiosoitteella ei löydy käyttäjää.</p></body></html>""")

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
        entity = ndb.Key(urlsafe=key).get()
        self.genericGetCollection(
            entity.__class__.gql(
                "WHERE archive_copy_of = KEY(:1) ORDER BY timestamp DESC",
                key))

class LoginStatusHandler(HardenedHandler):
    def get_(self, user):
        if user:
            info = {'logged_in': True,
                    'is_admin': users.is_current_user_admin(),
                    'nick': user.nickname(),
                    'email': str(user.email())}
            kennels = DatastoreClasses.Kennel.gql("WHERE kasvattaja_email = :1",
                                                  str(user.email()))
            if kennels.count() > 0:
                info['kennel'] = kennels.get().nimi
            self.jsonReply(info)
        else:
            self.jsonReply({
                    'logged_in': False,
                    'nick': None,
                    'email': None})

class PasswordRequestHandler(HardenedHandler):
    def post_unauthenticated_(self):
        if self.request.params['secret'] == "Suomen Partacolliet ry":
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
            message.sender = "partistietokanta@gmail.com"
            message.to = email
            message.subject = "Uusi salasana"
            message.body = ("""Hei!

Pyysit salasanaa Suomen Partacolliet ry:n jalostustietokantaan. 
Voit kirjautua tietokantaan tästä linkistä: <https://%s.appspot.com/LocalLoginRedirect?%s"""
                            % (app_identity.get_application_id(),
                               urllib.urlencode({'email': str(entry.email), 
                                                 'password': str(entry.password),
                                                 'redirect_url': ('https://%s.appspot.com/' 
                                                                  % app_identity.get_application_id())})))

                                                 
                               
            message.send()
            self.jsonReply({'email': '', 'nick': '', 'secret': '',
                            'status_message': 'Viesti matkalla'})

class CompactHistoryHandler(webapp2.RequestHandler):
    def post(self, key):
        top = ndb.Key(urlsafe=key).get()
        history = top.__class__.gql(
            "WHERE archive_copy_of = KEY(:1) ORDER BY timestamp DESC",
            key)
        to_delete = []
        for item in history:
            if top.subsumes(item):
                to_delete.append(item.key)
            else:
                # only compact top of history
                break
        logging.info("CompactHistory : delete %s" % to_delete)
        ndb.delete_multi(to_delete)

class ChangeNotificationCollectionHandler (HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('kennel'):
            self.genericGetCollection(
                DatastoreClasses.ChangeNotification.gql("WHERE kennel = :1 ORDER BY timestamp DESC",
                                                        self.request.params['kennel']))

DatastoreClasses.ChangeNotification.collectionHandler(ChangeNotificationCollectionHandler)

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
         DatastoreClasses.Kennel,
         DatastoreClasses.ChangeNotification,
         DatastoreClasses.SurveyQuestion,
         DatastoreClasses.Survey,
         DatastoreClasses.SurveySubmission,
         DatastoreClasses.SurveyAnswer,
         DatastoreClasses.SurveyAnswerSummary,
         DatastoreClasses.TerveyskyselySubmission,
         DatastoreClasses.YhdistysPaimennustaipumus])
    + [("/ModTime/([^/]+)", ModTimeHandler),
       ("/DepModTime/([^/]+)", DepModTimeHandler),
       ("/KoiraAutoComplete", KoiraAutoCompleteHandler),
       ("/History/([^/]+)", HistoryHandler),
       ("/FederatedLogin", FederatedLoginHandler),
       ("/LocalLogin", LocalLoginHandler),
       ("/LocalLoginRedirect", LocalLoginRedirectHandler),
       ("/Logout", LogoutHandler), 
       ("/LoginStatus", LoginStatusHandler),
       ("/PasswordRequest", PasswordRequestHandler),
       ("/CompactHistory/([^/]+)", CompactHistoryHandler),
       ("/Terveyskysely", Terveyskysely.TerveyskyselyCollectionHandler),
       ]
    + [webapp2.Route('/logout', handler='HardenedHandler.AuthHandler:logout', name='logout'),
       webapp2.Route('/auth/<provider>', 
                     handler='HardenedHandler.AuthHandler:_simple_auth', name='auth_login'),
       webapp2.Route('/auth/<provider>/callback', 
                     handler='HardenedHandler.AuthHandler:_auth_callback', name='auth_callback')]
    )

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'topsecretkey',
    }

app = webapp2.WSGIApplication(
    handler_list,
    config=config,
    debug=True)
