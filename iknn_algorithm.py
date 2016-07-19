# coding=utf-8
import sys
from rtree import index
from functions import *


def iknn(query_points, date_month, date_day, k_threshold):
    # Variables in dissertation
    candidate_set_c = []
    lambda_threshold = k_threshold

    # {trajectory:lower-bound similarity}
    # compute LB[] for all trajectories in candidate_set_c
    LB = {}

    list_lambda_points = {}  # for quick access to λ-NN(q_i)
    list_candidates = {}  # for quick access to C_i

    round_count = 0
    while True:
        key_count = 0
        for point in query_points:

            # line 7-8
            lambda_i_points, candidate_i = knn(point, date_month, date_day, lambda_threshold=lambda_threshold)

            list_candidates[key_count] = candidate_i
            list_lambda_points[key_count] = lambda_i_points
            key_count += 1

            # line 9
            for trajectory in candidate_i:
                candidate_set_c.append(trajectory)

        if len(candidate_set_c) > k_threshold:
            candidate_set_c = {}.fromkeys(candidate_set_c).keys()

            # Compute LB[] for all trajectories in C
            for trajectory in candidate_set_c:
                LB[trajectory] = compute_lb(trajectory, query_points, list_candidates, list_lambda_points)

            # sort top k and store trajectories
            k_LB = list(sorted(LB, key=LB.__getitem__, reverse=True))[0:k_threshold]

            # Compute UB_{n}
            UB_n = compute_ubn(query_points, list_lambda_points)

            # TODO 测试一下相似度
            # print 'sim', sim(query_points, 'data/user/P006000300000006/2014-07-22 r35.txt')

            if LB[k_LB[-1]] > UB_n:
                # compute UB for each candidate in C and sort candidate in C by UB in descending order
                return refine(candidate_set_c, query_points, list_candidates, list_lambda_points, k_threshold)

        # Increase λ by delta and go to the next round
        round_count += 1
        lambda_threshold += k_threshold * pow(2, round_count)


# Return λ-NN(q) & λ.top trajectories scanned by λ-NN(q)
# 根据查询点,返回λ-NN(q)和所有被扫描过的 λ.top() 条轨迹
def knn(point, date_month, date_day, lambda_threshold=10):
    # Initialize some variables
    idx = index.Index()

    query_longitude, query_latitude = point[0], point[1];
    trajectories = trajectories_of_date(date_month, date_day)

    # for-loop
    loop_count = 0
    for trajectory in trajectories:
        with open('%s/2014-%02d/%02d/%s' % ('data', date_month, date_day, trajectory), 'r') as f:
            for line in f:
                temp = line.strip('\n').split('\t')
                longitude, latitude, obd_time = float(temp[0]), float(temp[1]), int(temp[2])
                rtree_id = loop_count * pow(10, 11) + obd_time
                idx.insert(rtree_id, (longitude, latitude))
        loop_count += 1

    # λ-NN(q_i) = {q^1_i, q^2_i, ... q^λ_i}
    lambda_nn = []

    lambda_nearest = idx.nearest((query_longitude, query_latitude), lambda_threshold, objects=True)
    scanned_trajectories = []
    for item in lambda_nearest:
        lambda_nn.append([item.bbox[0], item.bbox[1]])
        file_index = item.id / pow(10, 11)  # get the position of file under the directory

        # the trajectory with specific date format of 2014-mm/dd
        scanned_trajectories.append('data/2014-%02d/%02d/%s' % (date_month, date_day, trajectories[file_index]))

    return lambda_nn, scanned_trajectories


# Compute similarity Sim(Q,R) between Q and R
def sim(query_points, trajectory):
    # The points in trajectory
    points_in_trajectory = []
    with open(trajectory, 'r') as f:
        for line in f:
            temp = line.strip('\n').split('\t')
            points_in_trajectory.append([float(temp[0]), float(temp[1])])

    ret_sum = 0
    for query_point in query_points:

        temp_min = sys.float_info.max
        for point_j in points_in_trajectory:
            temp_min = min(temp_min, distance_q_p(query_point, point_j))
        ret_sum += pow(math.e, (-1) * temp_min)

    return ret_sum


# Compute LB of similarity for each candidate R_x
def compute_lb(trajectory, query_points, list_candidates, list_lambda_points):
    # The points in trajectory
    points_in_trajectory = []
    with open(trajectory, 'r') as f:
        for line in f:
            temp = line.strip('\n').split('\t')
            points_in_trajectory.append([float(temp[0]), float(temp[1])])

    ret_lb = 0

    # i \in [1:m]
    for i in range(0, len(list_candidates)):
        if trajectory in list_candidates.get(i):  # R_{x} \in C_{i}
            temp_max, j = 0, 0
            for point in list_lambda_points.get(i):
                if point in points_in_trajectory:  # j \in [1:λ] and p^{j}_{i} \in R_{x}
                    temp_max = max(temp_max, pow(math.e, (-1) * distance_q_p(query_points[i], point)))
            ret_lb += temp_max
    return ret_lb


# Further define an upper bound UB of similarity for candidate trajectories in C only
def compute_ub(trajectory, query_points, list_candidates, list_lambda_points):
    # The points in trajectory
    points_in_trajectory = []
    with open(trajectory, 'r') as f:
        for line in f:
            temp = line.strip('\n').split('\t')
            points_in_trajectory.append([float(temp[0]), float(temp[1])])

    ret_lb_former, ret_lb_latter = 0, 0

    # i \in [1:m]
    for i in range(0, len(list_candidates)):
        if trajectory in list_candidates.get(i):  # R_{x} \in C_{i}
            temp_max, j = 0, 0
            for point in list_lambda_points.get(i):
                if point in points_in_trajectory:  # j \in [1:λ] and p^{j}_{i} \in R_{x}
                    temp_max = max(temp_max, pow(math.e, (-1) * distance_q_p(query_points[i], point)))
            ret_lb_former += temp_max
        else:
            ret_lb_latter += pow(math.e, (-1) * distance_q_p(query_points[i], list_lambda_points.get(i)[-1]))

    return ret_lb_former + ret_lb_latter


# Compute UB_{n} of similarity of all the non-scanned trajectories
def compute_ubn(query_points, list_lambda_points):
    ret_ubn, i = 0, 0
    for query_point in query_points:
        ret_ubn += pow(math.e, (-1) * distance_q_p(query_point, list_lambda_points.get(i)[-1]))
        i += 1

    return ret_ubn


# refinement procedure is triggered to examine the exact similarity of candidate trajectories are returned
def refine(candidate_set_c, query_points, list_candidates, list_lambda_points, k_threshold):
    ub = {}
    for trajectory in candidate_set_c:
        ub[trajectory] = compute_ub(trajectory, query_points, list_candidates, list_lambda_points)

    # k-best connected trajectories
    k_BCT = {}
    candidate = sorted(ub.items(), key=lambda t: t[1], reverse=True)
    for x in range(0, len(candidate)):
        sim_Rx = sim(query_points, candidate[x][0])
        if x <= k_threshold:
            k_BCT[candidate[x][0]] = sim_Rx
        else:
            temp_k_BCT = sorted(k_BCT.items(), key=lambda t: t[1])
            min_trajectory, k_BCT_min = temp_k_BCT[0]
            if sim_Rx > k_BCT_min:
                del k_BCT[min_trajectory]
                k_BCT[candidate[x][0]] = sim_Rx
            if x == len(candidate) - 1 or k_BCT_min >= compute_ub(candidate[x + 1][0], query_points, list_candidates,
                                                                  list_lambda_points):
                return sorted(k_BCT.items(), key=lambda t: t[1], reverse=True)


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

    flag = False
    for parent, dirnames, filenames in os.walk(prefix_path + directory_name):
        for item in filenames:
            if time_limit in item:
                flag = True
                res.append(item)

            if time_limit not in item and flag:
                break
    return res


# Return all the trajectory of a specific date
def trajectories_of_date(date_month, date_day, prefix_path='data/'):
    # directory : data/2014-mm/dd/
    return filename_in_dir('%s/2014-%02d/%02d' % (prefix_path, date_month, date_day))


qps = [[121.401576, 31.261853], [121.5032, 31.297063], [121.717433, 31.398219], [121.797771, 31.503072]]
print iknn(query_points=qps, date_month=7, date_day=19, k_threshold=15)

