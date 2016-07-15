# coding=utf-8
import os
import math
from rtree import index
from functions import *


# Algorithm 1:
def iknn(query_points, time_limit, k_threshold):
    # Variables in dissertation
    candidate_set_c = []
    LB = []  # compute LB[] for all trajectories in candidate_set_c
    lambda_threshold = k_threshold

    list_lambda_points = {}  # for quick access to λ-NN(q_i)
    list_candidates = {}  # for quick access to C_i

    key_count = 0
    for point in query_points:

        # line 7-8
        lambda_i_points, candidate_i = knn(point, time_limit, lambda_threshold=lambda_threshold)

        list_candidates[key_count] = candidate_i  # FIXME:这个地方的轨迹可能会比较少 需要在knn里面改进一下? 不然有些轨迹找不到
        list_lambda_points[key_count] = lambda_i_points
        key_count += 1

        # line 9
        for trajectory in candidate_i:
            candidate_set_c.append(trajectory)

    # print list_candidates
    if len(candidate_set_c) > k_threshold:
        candidate_set_c = {}.fromkeys(candidate_set_c).keys()

        for trajectory in candidate_set_c:
            print compute_lb(trajectory, query_points, list_candidates, list_lambda_points), trajectory
            LB.append(compute_lb(trajectory, query_points, list_candidates, list_lambda_points))

            # print list_candidates


# Return λ-NN(q) & λ.top trajectories scanned by λ-NN(q)
# 根据查询点,返回λ-NN(q)和所有被扫描过的 λ.top() 条轨迹
def knn(point, time_limit, lambda_threshold=10):
    # Initialize some variables
    idx = index.Index()

    query_longitude, query_latitude = point[0], point[1];
    users_directories = all_users_directories()

    # for-loop
    rtree_id_user = 0
    for directory in users_directories:
        user_trajectories = trajectories_of_user(directory_name=directory, time_limit=time_limit,
                                                 prefix_path='data/user/')
        rtree_id_trajectory = 0
        for trajectory in user_trajectories:
            with open('data/user/' + directory + '/' + trajectory, 'r') as f:
                for line in f:
                    temp = line.strip('\n').split('\t')
                    longitude, latitude, obd_time = float(temp[0]), float(temp[1]), temp[3]

                    # Construct the id of rtree
                    rtree_id = rtree_id_user * pow(10, 12) + rtree_id_trajectory * pow(10, 11) + time_transform_to_int(
                        obd_time)
                    idx.insert(rtree_id, (longitude, latitude))
            rtree_id_trajectory += 1
        rtree_id_user += 1

    # λ-NN(q_i) = {q^1_i, q^2_i, ... q^λ_i}
    lambda_nn = []
    # Format: {user: {trajectory: [time1, time2,...]}}
    record_dict = {}

    # Query with λ-nearest
    lambda_nearest = idx.nearest((query_longitude, query_latitude), lambda_threshold, objects=True)
    for item in lambda_nearest:

        lambda_nn.append([item.bbox[0], item.bbox[1]])
        user, trajectory, obd_time = item.id / pow(10, 12), item.id / pow(10, 11) % 10, item.id % pow(10, 11)

        if user not in record_dict:
            record_dict.setdefault(user, {})

        if trajectory not in record_dict[user]:
            record_dict[user].setdefault(trajectory, [])
        record_dict[user][trajectory].append(obd_time)

    # Trajectories scanned by λ-NN(q_i)
    scanned_trajectories = []
    for (user, v) in record_dict.iteritems():
        user = users_directories[user]

        trajectories = trajectories_of_user(directory_name=user, time_limit=time_limit, prefix_path='data/user/')
        for (trajectory, obd_time) in v.iteritems():
            scanned_trajectories.append('data/user/' + user + '/' + trajectories[trajectory])

    # Remove redundant trajectories
    return lambda_nn, {}.fromkeys(scanned_trajectories).keys()


# Compute LB of similarity for each candidate R_x
def compute_lb(trajectory, query_points, list_candidates, list_lambda_points):
    # The points in trajectory
    points_in_trajectory = []
    with open(trajectory, 'r') as f:
        for line in f:
            temp = line.strip('\n').split('\t')
            points_in_trajectory.append([float(temp[0]), float(temp[1])])

    ret_sum = 0

    # i \in [1:m]
    for i in range(0, len(list_candidates)):
        if trajectory in list_candidates.get(i):  # R_{x} \in C_{i}
            temp_max, j = 0, 0
            for point in list_lambda_points.get(i):
                if point in points_in_trajectory:  # j \in [1:λ] and p^{j}_{i} \in R_{x}
                    temp_max = max(temp_max, pow(math.e, (-1) * distance_q_p(query_points[i], point)))
            ret_sum += temp_max
    return ret_sum


# Return all the users under default directory 'data/user/
# 返回默认目录下的所有用户名
def all_users_directories(directory='data/user'):
    res = []
    for parent, dirnames, filenames in os.walk(directory):
        for item in dirnames:
            res.append(item)
    return res


# Return all the trajectory of a specific user by directory_name under default directory 'data/user/'
# 返回某一用户在规定时间 (默认是空值) 下的所有路径
def trajectories_of_user(directory_name, time_limit='', prefix_path='data/user/'):
    res = []
    for parent, dirnames, filenames in os.walk(prefix_path + directory_name):
        for item in filenames:
            if time_limit in item:
                res.append(item)
    return res


'''
---------------------------------------------
                    Sub
---------------------------------------------
'''


def res(filename):
    # with open('test/templl.txt', 'r') as fr, open('test/res.txt', 'w') as fw:
    #     for line in fr:
    #         temp = line.strip('\n').split('\t')
    #         fw.write('[%s,%s],\n' % (temp[0], temp[1]))

    with open(filename, 'r') as fr, open('test/res.txt', 'w') as fw:
        for line in fr:
            temp = line.strip('\n').split('\t')
            fw.write('[%s,%s],\n' % (temp[0], temp[1]))


qps = [[121.416769, 31.132241], [121.675635, 31.195697], [121.71546, 31.205094]]
iknn(query_points=qps, time_limit='2014-07-05', k_threshold=10)
# query_point = [121.424815, 31.041945]
# print knn(query_point, time_limit='2014-07-02', lambda_threshold=10)
# print len(str(time_transform_to_int('2014-07-04 23:09:20')))
# print time_transform_to_int('2014-07-04 23:09:20')
# print pow(10, 10)
