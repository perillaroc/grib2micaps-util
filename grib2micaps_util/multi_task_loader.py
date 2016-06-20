import subprocess
from multiprocessing import Pool
import os
import sys
import datetime
from xml.dom import minidom
from xml.dom import Node


class Config(object):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_dict = self.load_config()

    def load_config(self):
        config_dict = dict()
        doc = minidom.parse(self.config_path)
        root = doc.documentElement

        pool_size_node = root.getElementsByTagName('pool_size')[0]
        config_dict['pool_size'] = int(pool_size_node.firstChild.nodeValue)

        task_list_node = root.getElementsByTagName('task_list')[0]

        task_list = []
        for task_node in task_list_node.childNodes:
            if task_node.nodeType == Node.ELEMENT_NODE:
                one_task = {}
                for variable_node in task_node.childNodes:
                    if variable_node.nodeType == Node.ELEMENT_NODE:
                        one_task[variable_node.nodeName] = variable_node.firstChild.nodeValue

                task_list.append(one_task)

        config_dict['task_list'] = task_list

        return config_dict


def run_grib2micaps(no, task_param):

    print('start task {no} on {pid}...'.format(no=no, pid=os.getpid()))
    os.chdir(task_param['run_dir'])
    task_start_time = datetime.datetime.now()
    subprocess.run(
        [
            task_param['program'],
            task_param['start_time'],
            task_param['start_forecast_hour'],
            task_param['end_forecast_hour']
        ],
        stdout=None,
        stderr=None,
        shell=False
    )
    task_end_time = datetime.datetime.now()
    print('end task {no} on {pid} in {run_time}'.format(
        no=no,
        pid=os.getpid(),
        run_time=task_end_time - task_start_time
    ))


def main():
    print('Loader start...')
    loader_start_time = datetime.datetime.now()

    config = Config(os.path.dirname(__file__) + '/conf/multi_task_loader.config.xml')

    p = Pool(config.config_dict['pool_size'])

    for i in range(len(config.config_dict['task_list'])):
        p.apply_async(run_grib2micaps, args=(i, config.config_dict['task_list'][i]))

    p.close()
    p.join()

    loader_end_time = datetime.datetime.now()
    print("All task finished in {run_time}.".format(
        run_time=loader_end_time-loader_start_time
    ))


if __name__ == "__main__":
    main()