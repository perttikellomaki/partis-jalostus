import webapp2
from google.appengine.api import users
from google.appengine.api import oauth
import os
import json
import logging
from google.appengine.ext import db

PRODUCTION = not os.environ['SERVER_SOFTWARE'].startswith('Development')

class HardenedHandler(webapp2.RequestHandler):
    """Factors out common preconditions for get() and post() methods."""

    def get(self, *args, **kwargs):
        self.get_(users.get_current_user(),
                  *args, **kwargs)

    def post(self, *args, **kwargs):

        # Only authenticated users can post
        if users.get_current_user():
            path = self.request.path.split("/")
            if len(path) == 3:

                # This is a post with a key, e.g. ['', 'Koira', '1234']
                # Make a archive copy, which will be committed to datastore
                # in jsonReply() if the modification is successful.
                entity = db.get(path[2])
                self.archive_copy = entity.archive()
                logging.info("Created archive copy %s" % self.archive_copy)
                logging.info("archive_copy_of %s" % self.archive_copy.archive_copy_of)

            self.post_(users.get_current_user(),
                       *args, **kwargs)

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
