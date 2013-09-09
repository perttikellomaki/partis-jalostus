from HardenedHandler import HardenedHandler

class TerveyskyselyHandler(HardenedHandler):
    def post_(self, user):
        survey = Terveyskysely()
        survey.populateFromRequest(self.request.params)
        survey.sign(user)
        survey.put()

        message = mail.EmailMessage()
        message.sender = user.email()
        message.to = "pertti.kellomaki@gmail.com"
        message.subject = "Terveyskysely"
        message.body = ("Koira: %s\nautoimmuunisairaus: %s\nslo: %s\nimha: %s"
                        % (survey.virallinen_nimi,
                           survey.autoimmuunisairaus,
                           survey.slo,
                           survey.imha))
        message.send()
        
        self.jsonReply(survey.hashify())

