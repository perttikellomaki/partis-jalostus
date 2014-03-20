import webapp2
from webapp2_extras import sessions
from google.appengine.api import users
from google.appengine.api import oauth
from google.appengine.api import taskqueue
import os
import json
import logging
from google.appengine.ext import ndb

from simpleauth import SimpleAuthHandler

import DatastoreClasses

PRODUCTION = not os.environ['SERVER_SOFTWARE'].startswith('Development')

#Session Handling class, gets the store, dispatches the request
class BaseSessionHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class LocalUser(ndb.Model):
    email = ndb.StringProperty()
    nickname = ndb.StringProperty()
    password = ndb.StringProperty()

class UserProxy:
    """If the user is authenticated in the session using a local user entry,
a UserProxy is passed to the handlers instead of a Google users.user object."""
    
    def __init__(self, user_id, email, nickname):
        self.user_id_ = user_id
        self.email_ = email
        self.nickname_ = nickname

    def user_id(self):
        return self.user_id_

    def email(self):
        return self.email_

    def nickname(self):
        return self.nickname_

class HardenedHandler(BaseSessionHandler):
    """Factors out common preconditions for get() and post() methods."""

    def currentUser(self):
        user = users.get_current_user()
        if user:
            return user
        elif self.session.has_key('email') and self.session['email'] != '':
            return UserProxy(self.session['user_id'],
                             self.session['email'],
                             self.session['nickname'])
        else:
            return None

    def get(self, *args, **kwargs):
        user = self.currentUser()
        if user is None and "getUnauthenticated_" in self.__class__.__dict__:
            self.getUnauthenticated_(*args, **kwargs)
        else:
            self.get_(user, *args, **kwargs)

    def post(self, *args, **kwargs):

        if self.currentUser():
            # authenticated users can post
            path = self.request.path.split("/")
            if len(path) == 3:

                # This is a post with a key, e.g. ['', 'Koira', '1234']
                # Make a archive copy, which will be committed to datastore
                # in jsonReply() if the modification is successful.
                entity = ndb.Key(urlsafe=path[2]).get()
                if isinstance(entity, DatastoreClasses.SignedResource):
                    self.archive_copy = entity.archive()
                    logging.info("Created archive copy %s" % self.archive_copy)
                    logging.info("archive_copy_of %s" % self.archive_copy.archive_copy_of)

            self.post_(self.currentUser(),
                       *args, **kwargs)

        else:
            # there may be a handler for unauthenticated users
            self.post_unauthenticated_(*args, **kwargs)
            

    def delete(self, *args, **kwargs):

        # Only authenticated users can delete
        if users.get_current_user():
            self.delete_(users.get_current_user(),
                         *args, **kwargs)

    def jsonReply(self, data, debug_fmt=None):
        if debug_fmt:
            logging.info(debug_fmt % data)
        logging.info("jsonReply => %s" % data)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.dumps(data))
        try:
            # Possibly commit the archive copy created in self.post()
            self.archive_copy.put()
            #taskqueue.add(
            #    url=("/CompactHistory/%s" 
            #         % self.archive_copy.archive_copy_of.urlsafe()))
            self.archive_copy = None
        except:
            pass

    def genericGetCollection(self, collection, debug_fmt=None):
        data = []
        if self.request.params.has_key('modtime_only'):
            coll = [ndb.Key('Modtime', 'modtime', parent=key)
                    for key in collection]
        else:
            coll = collection
            
        for entity in coll:
            if isinstance(entity, ndb.Key):
                data.append(entity.get().hashify())
            else:
                data.append(entity.hashify())
        self.jsonReply(data, debug_fmt)


    def lookupKey(self, urlsafe=None, param=None):
        if urlsafe:
            key = ndb.Key(urlsafe=urlsafe)
        else:
            try:
                key = ndb.Key(urlsafe=self.request.params[param].split("/")[-1])
            except:
                key = None
        return key

class AuthHandler(BaseSessionHandler, SimpleAuthHandler):
    """Authentication handler for all kinds of auth."""

    def _on_signin(self, data, auth_info, provider):
        """Callback whenever a new or existing user is logging in.
        data is a user info dictionary.
        auth_info contains access token or oauth token and secret.
        """

        # record user data in session
        if data.has_key('email'):
            self.session['email'] = data['email']
        else:
            self.session['email'] = '%s@facebook.com' % data['username']
        self.session['user_id'] = 'facebook:%s' % data['id']
        self.session['nickname'] = data['name']

        self.redirect('/')

    def logout(self):
        self.auth.unset_session()
        self.redirect('/')

    def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider=provider, _full=True)

    def _get_consumer_info_for(self, provider):
        """Should return a tuple (key, secret) for auth init requests.
        For OAuth 2.0 you should also return a scope, e.g.
        ('my app id', 'my app secret', 'email,basic_info')
        
        The scope depends solely on the provider.
        See example/secrets.py.template
        """

        # Facebook info
        return ('278404465650592', '90f2cc4df139d75d3024a1d16f0da78c', 'user_about_me')

