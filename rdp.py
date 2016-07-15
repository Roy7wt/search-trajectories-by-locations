# coding=utf-8
# Assumption: the real distance between two points is equal to
# the difference in Longitude and Latitude
from math import radians, cos, sin, asin, sqrt
from object import Record


# Calculate the distance from a point to a line segment
def point_line_distance(p, start, end):

    # If the start point is the same as the end point
    if start.longitude == end.longitude and start.latitude == end.latitude:
        return sqrt(pow(p.longitude - start.longitude, 2) + pow(p.latitude - start.latitude, 2))

    n = float(abs((end.longitude - start.longitude) * (start.latitude - p.latitude) -
                  (start.longitude - p.longitude) * (end.latitude - start.latitude)))
    d = float(sqrt((end.longitude - start.longitude) * (end.longitude - start.longitude) +
                   (end.latitude - start.latitude) * (end.latitude - start.latitude)))

    return n / d


# Get the list of Points in record file
def list_of_points(filename):
    res = []
    with open(filename) as f:
        for line in f.readlines():
            longitude, latitude, velocity, time = line.strip('\n').split('\t')
            res.append(Record(float(longitude), float(latitude), float(velocity), time))
    f.close()
    return res


# Simplification Trajectory
def DouglasPeucker(points, start_index, end_index, epsilon=5e-03):
    index = start_index
    max_dist = 0

    for i in range(start_index + 1, end_index):
        temp_dist = point_line_distance(points[i], points[start_index], points[end_index])
        if temp_dist > max_dist:
            index = i
            max_dist = temp_dist

    if max_dist > epsilon:
        res1 = DouglasPeucker(points, start_index, index, epsilon)
        res2 = DouglasPeucker(points, index, end_index, epsilon)

        final_res = []
        for point_in_res1 in res1[:-1]:
            final_res.append(point_in_res1)
        for point_in_res2 in res2:
            final_res.append(point_in_res2)

        return final_res
    else:
        return [points[start_index], points[end_index]]
