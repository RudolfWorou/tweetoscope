class Cascade :
    def __init__(self, type , cid , msg , T_obs , tweets):

        self._type = type
        self._cid = cid
        self._msg = msg
        self._T_obs = T_obs
        self._tweets = tweets

    @property
    def cid(self):
        return self._cid

    @property
    def msg(self):
        return self._msg

    @property
    def T_obs(self):
        return self._T_obs

    @property
    def tweets(self):
        return self._tweets

    @property
    def source(self):
        return self._source
