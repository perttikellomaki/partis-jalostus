from HardenedHandler import HardenedHandler
from DatastoreClasses import YhdistysPaimennustaipumus

class YhdistysPaimennustaipumusCollectionHandler(HardenedHandler):
    def get_(self, user):
        koira = self.lookupKey(param='koira')
        self.genericGetCollection(
            YhdistysPaimennustaipumus.gql("WHERE koira = :1 AND archive_copy_of = NULL",
                                  koira))

    def post_(self, user):
        koira = self.lookupKey(param='koira')
        year, month, day = self.request.params['paiva'].split("-")
        paiva = datetime.date(int(year), int(month), int(day))
        test = YhdistysPaimennustaipumus(
            koira = koira,
            kiinnostus = int(self.request.params['kiinnostus']),
            taipumus = int(self.request.params['taipumus']),
            henkinen_kestavyys = int(self.request.params['henkinen_kestavyys']),
            ohjattavuus = int(self.request.params['ohjattavuus']),
            tuomari = self.request.params['tuomari'],
            paikka = self.request.params['paikka'],
            paiva = paiva)
        test.sign(user)
        test.put()
        self.jsonReply(test.hashify())

YhdistysPaimennustaipumus.collectionHandler(YhdistysPaimennustaipumusCollectionHandler)

class YhdistysPaimennustaipumusHandler(HardenedHandler):
    def post_(self, user, key):
        test = self.lookupKey(urlsafe=key).get()
        year, month, day = self.request.params['paiva'].split("-")
        paiva = datetime.date(int(year), int(month), int(day))
        test.kiinnostus = int(self.request.params['kiinnostus'])
        test.taipumus = int(self.request.params['taipumus'])
        test.henkinen_kestavyys = int(self.request.params['henkinen_kestavyys'])
        test.ohjattavuus = int(self.request.params['ohjattavuus'])
        test.tuomari = self.request.params['tuomari']
        test.paikka = self.request.params['paikka']
        test.paiva = paiva
        test.sign(user)
        test.put()
        self.jsonReply(test.hashify())

YhdistysPaimennustaipumus.individualHandler(YhdistysPaimennustaipumusHandler)
