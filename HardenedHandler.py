import webapp2
from webapp2_extras import sessions
from google.appengine.api import users
from google.appengine.api import oauth
import os
import json
import logging
from google.appengine.ext import db

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

class LocalUser(db.Model):
    email = db.StringProperty()
    nickname = db.StringProperty()
    password = db.StringProperty()

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
        self.get_(self.currentUser(),
                  *args, **kwargs)

    def post(self, *args, **kwargs):

        if self.currentUser():
            # authenticated users can post
            path = self.request.path.split("/")
            if len(path) == 3:

                # This is a post with a key, e.g. ['', 'Koira', '1234']
                # Make a archive copy, which will be committed to datastore
                # in jsonReply() if the modification is successful.
                entity = db.get(path[2])
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

    def jsonReply(self, data):
        logging.info("jsonReply => %s" % data)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.dumps(data))
        try:
            # Possibly commit the archive copy created in self.post()
            self.archive_copy.put()
            self.archive_copy = None
        except:
            pass
