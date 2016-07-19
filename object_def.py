# coding=utf-8
# The basic information of a point on a trajectory


class Record(object):
    def __init__(self, longitude, latitude, obd_time):
        self._longitude = longitude
        self._latitude = latitude
        self._obd_time = obd_time

    @property
    def longitude(self):
        return self._longitude

    @property
    def latitude(self):
        return self._latitude

    @property
    def obd_time(self):
        return self._obd_time

    pass
