import logging
from google.appengine.api import users
from google.appengine.ext import ndb
from HardenedHandler import HardenedHandler
from DatastoreClasses import Kennels, Kennel
import Util

class KennelCollectionHandler(HardenedHandler):
    def get_(self, user):
        self.genericGetCollection(
            Kennel.gql("ORDER BY nimi"))

    def post_(self, user):
        if users.is_current_user_admin():
            parent = Kennels.getSingleton()
            kennel = Kennel(parent=parent)
            kennel.populateFromRequest(self.request.params)
            kennel.canonical_name = Util.canonical(kennel.nimi)
            kennel.Put()
            self.jsonReply(kennel.hashify())
        else:
            self.response.set_status(403)
            self.response.out.write("Access denied.")


Kennel.collectionHandler(KennelCollectionHandler)

class KennelHandler (HardenedHandler):
    def get_(self, user, key):
        kennel = ndb.Key(urlsafe=key).get()
        self.jsonReply(kennel.hashify())

    def post_(self, user, key):
        if users.is_current_user_admin():
            kennel = ndb.Key(urlsafe=key).get()
            kennel.populateFromRequest(self.request.params)
            kennel.canonical_name = Util.canonical(kennel.nimi)
            kennel.Put()
            self.jsonReply(kennel.hashify())
        else:
            self.response.set_status(403)
            self.response.out.write("Access denied.")
        

Kennel.individualHandler(KennelHandler)
