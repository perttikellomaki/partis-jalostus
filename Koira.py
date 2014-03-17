import logging
from google.appengine.ext import ndb
from HardenedHandler import HardenedHandler
from DatastoreClasses import Koira, KoiraAutocomplete, ChangeNotification, Kennel
import Util

class KoiraCollectionHandler(HardenedHandler):
    def get_(self, user):
        if (self.request.params.has_key('sukupuoli')
            and self.request.params['sukupuoli'] != ''
            and self.request.params['sukupuoli'] != 'undefined'):
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL AND sukupuoli = :1 ORDER BY virallinen_nimi ASC",
                            self.request.params['sukupuoli'])
        elif (self.request.params.has_key('kennel')
            and self.request.params['kennel'] != ''
            and self.request.params['kennel'] != 'undefined'):
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL AND kennel = :1 ORDER BY virallinen_nimi ASC",
                            self.request.params['kennel'])
        elif self.request.params.has_key('virallinen_nimi'):
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL AND virallinen_nimi = :1",
                            self.request.params['virallinen_nimi'])
        else:
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL ORDER BY virallinen_nimi ASC")

        self.genericGetCollection(query, "KoiraCollectionHandler ==> %s")

    def post_(self, user):
        dog = Koira()
        dog.populateFromRequest(self.request.params)
        dog.canonical_name = Util.canonical(dog.virallinen_nimi)
        dog.sign(user)

        for kennel in Kennel.query():
            if dog.canonical_name.startswith(kennel.canonical_name):
                dog.kennel = kennel.nimi
                break;

        dog.Put()

        autocomplete = KoiraAutocomplete(
            id="autocomplete", 
            virallinen_nimi=dog.virallinen_nimi,
            canonical = dog.canonical_name,
            uros = dog.sukupuoli == 'uros',
            parent=dog.key)
        autocomplete.put()

        ChangeNotification(kennel=dog.kennel, 
                           is_creation=True, 
                           koira=dog.key, 
                           changed_entity=dog.key,
                           author_nick=user.nickname()).put()

        self.jsonReply(dog.hashify())

Koira.collectionHandler(KoiraCollectionHandler)

class KoiraHandler(HardenedHandler):
    def get_(self, user, urlsafe):
        key = self.lookupKey(urlsafe=urlsafe)
        logging.info("key: %s" % key)
        if self.request.params.has_key('modtime'):
            entry_key = ndb.Key('Modtime', 'modtime', parent=key)
            logging.info("entry_key: %s" % entry_key)
            entry = entry_key.get()
            self.jsonReply(entry.hashify())
        else:
            dog = key.get()

            # FIXME: remove when all dogs have a canonical name
            dog.canonical_name = Util.canonical(dog.virallinen_nimi)
            dog.put()

            self.jsonReply(dog.hashify())

    def post_(self, user, key):
        dog = ndb.Key(urlsafe=key).get()
        original_kennel = dog.kennel
        name = dog.virallinen_nimi
        sex = dog.sukupuoli
        dog.populateFromRequest(self.request.params)
        dog.verified = False
        dog.sign(user, self.request, dog.key)
        dog.Put()
        if dog.virallinen_nimi != name or dog.sukupuoli != sex:
            auto = ndb.Key('KoiraAutocomplete', 'autocomplete', parent=dog.key).get()
            auto.virallinen_nimi = dog.virallinen_nimi
            auto.canonical = dog.canonical_name()
            auto.uros = dog.sukupuoli == 'uros'
            auto.put()

        if (original_kennel is not None 
            and original_kennel != ''
            and original_kennel != dog.kennel):
            
            # kennel changed, create notification for both original and new kennel
            ChangeNotification(kennel=original_kennel, 
                               koira=dog.key, 
                               changed_entity=dog.key,
                               author_nick=user.nickname()).put()

        ChangeNotification(kennel=dog.kennel,
                           koira=dog.key, 
                           changed_entity=dog.key,
                           author_nick=user.nickname()).put()

        self.jsonReply(dog.hashify())

Koira.individualHandler(KoiraHandler)
