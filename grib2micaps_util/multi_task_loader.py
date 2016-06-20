import subprocess
from multiprocessing import Pool
import os
import sys
import datetime

program_dir_path = 'D:/windroc/project/2016/grib2micaps/grapesGfs_grib2micaps_v3.9.4'
program_file_name = 'grib2micaps.exe'


def run_grib2micaps(no, date, start_hour, end_hour):
    print('start task {no} on {pid}...'.format(no=no, pid=os.getpid()))
    os.chdir(program_dir_path+'_{no}'.format(no=no))
    task_start_time = datetime.datetime.now()
    subprocess.run([program_file_name, date, start_hour, end_hour],
                   stdout=None, stderr=None,
                   shell=True)
    task_end_time = datetime.datetime.now()
    print('end task {no} on {pid} in {run_time}'.format(
        no=no,
        pid=os.getpid(),
        run_time=task_end_time - task_start_time
    ))


def main():
    print('Loader start...')
    loader_start_time = datetime.datetime.now()
    os.chdir(program_dir_path)

    p = Pool(2)

    args_list = [
        (0, '2016061708', '0', '3'),
        (1, '2016061708', '6', '9'),
    ]

    for i in range(2):
        p.apply_async(run_grib2micaps, args=args_list[i])
    p.close()
    p.join()
    loader_end_time = datetime.datetime.now()
    print("All task finished in {run_time}.".format(
        run_time=loader_end_time-loader_start_time
    ))


if __name__ == "__main__":
    main()