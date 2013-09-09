import logging
from google.appengine.ext import ndb
from HardenedHandler import HardenedHandler
from DatastoreClasses import Koira

class KoiraCollectionHandler(HardenedHandler):
    def get_(self, user):
        if (self.request.params.has_key('sukupuoli')
            and self.request.params['sukupuoli'] != ''
            and self.request.params['sukupuoli'] != 'undefined'):
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL AND sukupuoli = :1 ORDER BY virallinen_nimi ASC",
                            self.request.params['sukupuoli'])
        elif self.request.params.has_key('virallinen_nimi'):
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL AND virallinen_nimi = :1",
                            self.request.params['virallinen_nimi'])
        else:
            query = ndb.gql("SELECT __key__ FROM Koira WHERE archive_copy_of = NULL ORDER BY virallinen_nimi ASC")

        self.genericGetCollection(query)

    def post_(self, user):
        dog = Koira()
        dog.populateFromRequest(self.request.params)
        dog.sign(user)
        dog.Put()

        autocomplete = KoiraAutocomplete(
            id="autocomplete", 
            virallinen_nimi=dog.virallinen_nimi,
            canonical = dog.virallinen_nimi.lower(),
            uros = dog.sukupuoli == 'uros',
            parent=dog.key)
        autocomplete.put()
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
            self.jsonReply(dog.hashify())

    def post_(self, user, key):
        dog = ndb.Key(urlsafe=key).get()
        name = dog.virallinen_nimi
        sex = dog.sukupuoli
        dog.populateFromRequest(self.request.params)
        dog.sign(user)
        dog.Put()
        if dog.virallinen_nimi != name or dog.sukupuoli != sex:
            auto = ndb.Key('KoiraAutocomplete', 'autocomplete', parent=dog.key).get()
            auto.virallinen_nimi = dog.virallinen_nimi
            auto.canonical = dog.virallinen_nimi.lower()
            auto.uros = dog.sukupuoli == 'uros'
            auto.put()

        self.jsonReply(dog.hashify())

Koira.individualHandler(KoiraHandler)
