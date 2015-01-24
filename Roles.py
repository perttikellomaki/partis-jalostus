import logging
from google.appengine.ext import ndb
from google.appengine.api import users
from HardenedHandler import HardenedHandler
from DatastoreClasses import Role

class RoleCollectionHandler(HardenedHandler):
    def get_(self, user):
        roles = []
        if users.is_current_user_admin():
            roles.append(Role(user_id = user.user_id(),
                              role = 'application_admin'))
        self.jsonReply([role.hashify() for role in roles])

Role.collectionHandler(RoleCollectionHandler)

            
