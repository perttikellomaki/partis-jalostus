import logging
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import users
from HardenedHandler import HardenedHandler
from DatastoreClasses import Role, DogOwnerRole, TerveyskyselySubmission, Profile

class RoleCollectionHandler(HardenedHandler):
    def get_(self, user):
        if self.request.params.has_key('user_id'):
            user_id = self.request.params['user_id']
        else:
            user_id = user.user_id()
        data = []
        if users.is_current_user_admin():
            data.append(Role(user_id=user_id, role='admin', valid=True).hashify())
        for role in ndb.gql("SELECT * FROM Role WHERE user_id=:1 AND valid=true", user_id):
            data.append(role.hashify())
        self.jsonReply(data)

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
                    deferred.defer(dogOwnerRoleConfirmed, entity.key, entity.user_id)
                entity.Put()
                self.jsonReply(entity.hashify())
        else:
            self.request.set_status(401)

DogOwnerRole.individualHandler(DogOwnerRoleIndividualHandler)

def dogOwnerRoleConfirmed (role_key, user_id):
    role = role_key.get()
    profile_key = Profile.byUserId(user_id)
    query = TerveyskyselySubmission.gql("WHERE koira = :1 and answered_by = :2", role.dog, profile_key)
    for submission in query:
        logging.info("roleConfirmed: %s" % submission)
        submission.owner_confirmed = True
        submission.Put()

