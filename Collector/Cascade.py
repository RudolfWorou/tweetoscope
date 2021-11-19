'''
Nous définissons dans ce fichier un modèle classique de la classe Cascade.
'''
class Cascade :
    def __init__(self, type , cid , msg , tweets):

        self._type = type
        self._cid = cid
        self._msg = msg
        self._tweets = tweets

    @property
    def cid(self):
        return self._cid

    @property
    def msg(self):
        return self._msg

    @property
    def tweets(self):
        return self._tweets

    @property
    def source(self):
        return self._source
