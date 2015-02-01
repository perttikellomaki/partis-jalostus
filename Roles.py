import logging
from google.appengine.ext import ndb
from google.appengine.api import users
from HardenedHandler import HardenedHandler
from DatastoreClasses import Role, DogOwnerRole

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

class DogOwnerRoleCollectionHandler (HardenedHandler):
    def get_(self, user):
        if users.is_current_user_admin():
            if self.request.params.has_key('valid'):
                self.genericGetCollection(ndb.gql("SELECT __key__ FROM DogOwnerRole WHERE valid=:1", self.request.params['valid'] == 'true'), "==> %s")
            else:
                self.genericGetCollection(ndb.gql("SELECT __key__ FROM DogOwnerRole"))
        else:
            self.request.set_status(401)


DogOwnerRole.collectionHandler(DogOwnerRoleCollectionHandler)

class DogOwnerRoleIndividualHandler (HardenedHandler):
    def get_(self, user, key):
        if users.is_current_user_admin():
            self.genericIndividualGet(user, key)
        else:
            self.request.set_status(401)

    def post_(self, user, key):
        if users.is_current_user_admin():
            entity = ndb.Key(urlsafe=key).get()
            if entity:
                was_valid = entity.valid
                entity.populateFromRequest(self.request.Params)
                if entity.valid and not was_valid:
                    confirmer = ndb.Key('Profile', user.user_id())
                    entity.confirmed_by = confirmer
                    pending_survey = entity.pending_survey.get()
                    if pending_survey:
                        pending_survey.owner_confirmed = True
                        pending_survey.Put()
                entity.Put()
                self.jsonReply(entity.hashify())
        else:
            self.request.set_status(401)

DogOwnerRole.individualHandler(DogOwnerRoleIndividualHandler)
