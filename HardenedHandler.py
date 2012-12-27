import webapp2
from google.appengine.api import users
from google.appengine.api import oauth
import os
import json
import logging

whitelist = ["114665306391201355583"    #pertti.kellomaki@gmail.com
             ,"118338434270422837552"   #clickercontestinguser@gmail.com
             ,"112756918201578659628"   #mkellomaki@gmail.com
             ]

PRODUCTION = not os.environ['SERVER_SOFTWARE'].startswith('Development')

class HardenedHandler(webapp2.RequestHandler):
    """Factors out common preconditions for get() and post() methods."""

    def get(self, *args, **kwargs):
        if (not PRODUCTION) or (users.get_current_user() and users.get_current_user().user_id() in whitelist):
            self.get_(users.get_current_user(),
                      *args, **kwargs)
        else:
            # These will throw exceptions if the user has not
            # authenticated with oauth, or if there is no
            # oauthGet_ method.
            user = oauth.get_current_user()
            self.oauthGet_(user, *args, **kwargs)

    def post(self, *args, **kwargs):
        if (not PRODUCTION) or (users.get_current_user() and users.get_current_user().user_id() in whitelist):
            self.post_(users.get_current_user(),
                       *args, **kwargs)
        else:
            # These will throw exceptions if the user has not
            # authenticated with oauth, or if there is no
            # oauthPost_ method.
            user = oauth.get_current_user()
            self.oauthPost_(user, *args, **kwargs)

    def delete(self, *args, **kwargs):
        if (not PRODUCTION) or (users.get_current_user() and users.get_current_user().user_id() in whitelist):
            self.delete_(users.get_current_user(),
                         *args, **kwargs)

    def jsonReply(self, data):
        logging.info("jsonReply => %s" % data)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.dumps(data))
