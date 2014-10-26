from google.appengine.ext import ndb

from HardenedHandler import HardenedHandler
from DatastoreClasses import Survey

terveyskysely_key = ndb.Key(Survey, 'terveyskysely')

class TerveyskyselyCollectionHandler (HardenedHandler):
    def get_(self, user):
        kysely = terveyskysely_key.get()
        if kysely is None:
            kysely = Survey(key=terveyskysely_key, title="Terveyskysely")
            kysely.Put()
        result = [kysely.hashify()]
        self.jsonReply(result)
