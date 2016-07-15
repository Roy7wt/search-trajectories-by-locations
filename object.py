# coding=utf-8
# The basic information of a point on a trajectory


class Record(object):
    def __init__(self, longitude, latitude, velocity, obd_time):
        self._longitude = longitude
        self._latitude = latitude
        self._velocity = velocity
        self._obd_time = obd_time

    @property
    def longitude(self):
        return self._longitude

    @property
    def latitude(self):
        return self._latitude

    @property
    def velocity(self):
        return self._velocity

    @property
    def obd_time(self):
        return self._obd_time

    pass
