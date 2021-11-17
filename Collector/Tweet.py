class Tweet :
    def __init__(self, type = "", msg = "", time = 0, magnitude = 0, source = "", info = ""):

        self._type = type
        self._msg = msg
        self._time = time
        self._magnitude = magnitude
        self._source = source
        self._info = info

    @property
    def type(self):
        return self._type

    @property
    def msg(self):
        return self._msg

    @property
    def time(self):
        return self._time

    @property
    def magnitude(self):
        return self._magnitude

    @property
    def source(self):
        return self._source

    @property
    def info(self):
        return self._info