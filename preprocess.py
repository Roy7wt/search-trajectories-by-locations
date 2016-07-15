# coding=utf-8

from rdp import *
from object import Record
from functions import *


# Generate all the trajectories of a user and store
def func():
    obd_dict = {'SEQUENCE': 0, 'OBD_NUM': 2, 'LONGITUDE': 3, 'LATITUDE': 4, 'VELOCITY': 5, 'OBD_TIME': 8}
    with open('file/vehicle_gps_log_2014-07.txt', 'r') as obd_file:
        for line in obd_file:

            temp = line.strip('\n').split(',')
            obd_num = temp[obd_dict['OBD_NUM']]
            res = [temp[obd_dict['LONGITUDE']], temp[obd_dict['LATITUDE']], temp[obd_dict['VELOCITY']],
                   temp[obd_dict['OBD_TIME']]]

            longitude = res[0]
            latitude = res[1]

            # Longitude and Latitude Of Shanghai
            # 上海的经纬度范围
            if 119.5 < float(longitude) < 123.5 and 30.5 < float(latitude) < 32.5:
                with open('data/%s/2014-07_%s.txt' % ('shanghai', obd_num), 'a+') as f:

                    # Read the last Record time
                    if f.tell() != 0:
                        f.seek(-20, 1)
                        last_timestamp = f.read(19)

                        # If the time difference satisfies the conditions, separate the trajectory
                        if time_difference(res[3], last_timestamp) > 1800:
                            f.write('\n')

                    # Write the record
                    length = len(res)
                    for i in range(0, length):
                        if i == 0 or i == 1:
                            f.write(str(round(float(res[i]), 6)))
                        else:
                            f.write(res[i])

                        if i != length - 1:
                            f.write('\t')
                        else:
                            f.write('\n')

    obd_file.close()


# 将某一个用户的当月的所有轨迹划分成单条轨迹
def simplification_trajectory_per_user():
    root_dir = "data/shanghai/"
    for filename in filename_in_dir(root_dir):
        user_id = filename[8:24]
        if os.path.exists('data/user/%s' % user_id):
            pass
        else:
            os.mkdir('data/user/%s' % user_id)

        cnt = -1
        trajectory_points = []
        with open("data/shanghai/" + filename, 'r') as f:
            for line in f.readlines():
                if line == '\n':
                    cnt += 1
                    dp_list = DouglasPeucker(trajectory_points, 0, len(trajectory_points) - 1)
                    # print len(trajectory_points)
                    # print len(dp_list)
                    # print 'pass'

                    with open('data/user/%s/%s r%d.txt' % (user_id, dp_list[0].obd_time[0:10], cnt), 'w') as fw:
                        for item in dp_list:
                            # TODO: 这里存时间的格式还是字符串格式 可以换成int或long类型来减少存储空间 同时前面的obd_time[]也要换掉
                            # fw.write('[%f,%f],\n' % (item.longitude, item.latitude))
                            fw.write('%f\t%f\t%d\t%s\n' % (item.longitude, item.latitude, item.velocity, item.obd_time))

                    fw.close()
                    trajectory_points = []
                else:
                    longitude, latitude, velocity, obd_time = line.strip('\n').split('\t')
                    trajectory_points.append(Record(float(longitude), float(latitude),
                                                    int(velocity), obd_time))

# func()  # 第一步
simplification_trajectory_per_user()  # 第二步
# print time_transform("2014-07-01 03:08:49")-time_transform("2014-07-01 03:09:09")
# print time_difference("2014-07-01 01:21:39", "2014-07-01 01:21:45")
# func2("data/shanghai")
