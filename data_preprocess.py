# coding=utf-8

from object_def import Record
from dp_algorithm import *
from functions import *

# Global parameters
raw_data_path = 'data/vehicle_gps_log_2014-07.txt'
district = 'shanghai'
date = '2014-07'
epsilon = 5e-03


# Generate all the trajectories of a user and store them
def generate_trajectories():
    obd_dict = {'OBD_NUM': 2, 'LONGITUDE': 3, 'LATITUDE': 4, 'OBD_TIME': 8}

    with open(raw_data_path, 'r') as obd_file:
        for line in obd_file:
            temp = line.strip('\n').split(',')
            obd_num = temp[obd_dict['OBD_NUM']]
            data_arr = [temp[obd_dict['LONGITUDE']], temp[obd_dict['LATITUDE']], temp[obd_dict['OBD_TIME']]]

            # Get the longitude and latitude of each record
            longitude = data_arr[0]
            latitude = data_arr[1]

            # Select record within the range of Shanghai by longitude and latitude
            if 119.5 < float(longitude) < 123.5 and 30.5 < float(latitude) < 32.5:
                with open('data/%s/2014-07_%s.txt' % ('shanghai', obd_num), 'a+') as f:

                    # Read the last Record time
                    if f.tell() != 0:
                        f.seek(-20, 1)
                        last_timestamp = f.read(19)

                        # If the time difference satisfies the conditions, separate the trajectory
                        if time_difference(data_arr[2], last_timestamp) > 1800:
                            f.write('\n')

                    # Write the record
                    length = len(data_arr)
                    for i in range(0, length):
                        if i == 0 or i == 1:
                            f.write(str(round(float(data_arr[i]), 6)))
                        else:
                            f.write(data_arr[i])

                        if i != length - 1:
                            f.write('\t')
                        else:
                            f.write('\n')


# Append a '\n' for in the end each user
def append_n(district_name):
    for filename in filename_in_dir('data/' + district_name):
        with open('data/' + district_name + '/' + filename, 'a') as f:
            f.write('\n')


def simplification_trajectories_per_user(district_name, para_epsilon):
    for filename in filename_in_dir('data/' + district_name):
        user_id = filename[8:24]
        if not os.path.exists('data/user/%s' % user_id):
            os.mkdir('data/user/%s' % user_id)

        route_count = -1
        trajectory_points = []
        with open('data/' + district_name + '/' + filename, 'r') as f:
            for line in f.readlines():
                if line == '\n':
                    route_count += 1
                    dp_list = DouglasPeucker(trajectory_points, 0, len(trajectory_points) - 1, epsilon=para_epsilon)

                    with open('data/user/%s/%s r%d.txt' % (user_id, dp_list[0].obd_time[0:10], route_count), 'w') as fw:
                        for record in dp_list:
                            fw.write('%f\t%f\t%d\n' % (
                                record.longitude, record.latitude, time_transform_to_int(record.obd_time)))

                        # reset the list for next round storing
                        trajectory_points = []

                else:
                    longitude, latitude, obd_time = line.strip('\n').split('\t')
                    trajectory_points.append(Record(float(longitude), float(latitude), obd_time))


# data: yyyy-MM
def sort_trajectories_by_date(para_date):
    # Construct the directory yyyy-MM
    if not os.path.exists('data/%s' % para_date):
        os.mkdir('data/%s' % para_date)

        # TODO 因为知道是七月 所以是31天 可以写一个函数来解决这个问题 这里为了方便还是规定了31
        for day_of_month in range(1, 32):
            os.mkdir('data/%s/%02d' % (para_date, day_of_month))

    for directory in dirname_in_dir('data/user'):
        for filename in filename_in_dir('data/user/%s' % directory):
            date_month, date_day, route_count = filename[0:7], filename[8:10], filename[11:-4]
            with open('data/user/%s/%s' % (directory, filename), 'r') as fr, open(
                            'data/%s/%s/%s %s' % (date_month, date_day, directory, route_count), 'w') as fw:
                for line in fr:
                    fw.write(line)


# generate_trajectories()
# append_n(district_name=district)
# simplification_trajectories_per_user(district_name=district, para_epsilon=epsilon)
# sort_trajectories_by_date(para_date=date)
