# Configuration file


# Email configuration
class Email:
    def __init__(self):
        self.send_from = 'luke.a.stegeman@nasa.gov'
        self.reply_to = 'luke.a.stegeman@nasa.gov'
        self.server = 'ndc-relay.ndc.nasa.gov'
email = Email()


class Path:
    def __init__(self):
        self.report = './reports/'
path = Path()



