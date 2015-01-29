import logging
from google.appengine.ext import ndb
from google.appengine.api import users
from HardenedHandler import HardenedHandler
from DatastoreClasses import Role

class RoleCollectionHandler(HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('user_id'):
            user_id = self.request.params['user_id']
        else:
            user_id = user.user_id()
        self.genericGetCollection(ndb.gql("SELECT __key__ FROM Role WHERE user_id=:1 AND valid=true", user_id))

    def post_(self, user):
        if users.is_current_user_admin():
            role = Role()
            role.populateFromRequest(self.request.Params)
            role.valid = True
            role.put()
        else:
            self.request.set_status(401)

Role.collectionHandler(RoleCollectionHandler)

            
