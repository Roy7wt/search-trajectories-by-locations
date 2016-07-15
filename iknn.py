# coding=utf-8
import os
from rtree import index
from functions import *


# Algorithm 1:
def iknn(query_points, time_limit, k_threshold):
    candidate_set_c = []
    list_cadidate_i = []  # for quick access to C_i
    lambda_threshold = k_threshold
    round_cnt = 0

    LB = []  # compute LB[] for all trajectories in candidate_set_c
    while True:
        round_cnt += 1

        for point in query_points:
            candidate_i = knn(point, time_limit, lambda_threshold=lambda_threshold)
            list_cadidate_i.append(candidate_i)
            for trajectory in candidate_i:
                candidate_set_c.append(trajectory)  # C <- C1 ∪ C2 ∪ ... ∪ Cm

        if len(candidate_set_c) > k_threshold:
            for candidate in candidate_set_c:
                similarity_sum = 0
                for trajectory in candidate:


        else:
            lambda_threshold += k_threshold * pow(2, round_cnt)


# 根据查询点,返回所以被扫描过的 λ.top()条轨迹
def knn(point, time_limit, lambda_threshold=10):
    # Initialize some variables
    idx = index.Index()
    query_longitude, query_latitude = point[0], point[1];

    # for-loop
    users_directories = all_users_directories()
    # 构造id
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

    # Query with λ-nearest
    res = idx.nearest((query_longitude, query_latitude), lambda_threshold, objects=True)


    lambda_nn = [] # {p^1_i, p^2_i, ..., p^λ_i}
    record_dict = {}
    for item in res:

        user, trajectory, obd_time = item.id / pow(10, 12), item.id / pow(10, 11) % 10, item.id % pow(10, 11)
        if user not in record_dict:
            record_dict.setdefault(user, {})

        if trajectory not in record_dict[user]:
            record_dict[user].setdefault(trajectory, [])
        record_dict[user][trajectory].append(obd_time)

    # TODO (删除)
    # 输出一下现在字典里面的数据
    # print record_dict

    # Trajectories scanned by λ-NN(q_i)
    scanned_trajectories = []
    for (user, v) in record_dict.iteritems():
        user = users_directories[user]

        trajectories = trajectories_of_user(directory_name=user, time_limit=time_limit, prefix_path='data/user/')
        for (trajectory, obd_time) in v.iteritems():
            scanned_trajectories.append('data/user/' + user + '/' + trajectories[trajectory])

    # Remove redundant trajectories
    return {}.fromkeys(scanned_trajectories).keys()


# Compute LB of similarity for each candidate R_x
# def LB(trajectory, query_points):


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
Sub
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


# qps = [[121.652006, 31.196866], [120.9736, 32.060969]]
# iknn(query_points=qps, time_limit='2014-07-05', k_threshold=20)
query_point = [121.424815, 31.041945]
print knn(query_point, time_limit='2014-07-02', lambda_threshold=10)
# print len(str(time_transform_to_int('2014-07-04 23:09:20')))
# print time_transform_to_int('2014-07-04 23:09:20')
# print pow(10, 10)
