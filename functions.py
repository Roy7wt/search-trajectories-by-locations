# coding=utf-8

import os
import math
import time


# Transform the timestamp in form of 'yyyy-mm-dd HH:MM:SS' into int format.
# 时间戳'yyyy-mm-dd HH:MM:SS'转换为整数
def time_transform_to_int(timestamp):
    time_array = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    return int(time.mktime(time_array))


# Transform the timestamp into 'yyyy-mm-dd HH:MM:SS'
# 时间戳 整数转换成 'yyyy-mm-dd HH:MM:SS'
def time_transform_to_str(timestamp):
    time_array = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_array)


# Latter - former
# 时间做差
def time_difference(ts_latter, ts_former):
    return time_transform_to_int(ts_latter) - time_transform_to_int(ts_former)


# All the files under the root dir
def filename_in_dir(root_dir):
    temp_files = []
    for parent, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            temp_files.append(filename)
    return temp_files


# All the directory under the root dir
def dirname_in_dir(root_dir):
    temp_dirs = []
    for parent, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            temp_dirs.append(dirname)
    return temp_dirs


# Distance between two points(longitude, latitude)
def distance_q_p(query, point):
    return math.sqrt(pow(query[0] - point[0], 2) + pow(query[1] - point[1], 2))
