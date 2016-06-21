import argparse
import datetime
from multiprocessing import Pool
import os
import subprocess
from xml.dom import minidom
from xml.dom import Node

"""
config file 的层次结构
    multi_task_loader:

        pool_size：int，同时运行的进程数
            注意： task_list 中的 task 个数可以大于 pool_size

        task_list：由多个 task 节点组成，表示同时运行的任务列表
            task
                start_time: YYYYMMDDHH，起报时间
                start_forecast_hour: HH，转码的起始时效
                end_forecast：HH，转码的终止时效
                run_dir：程序运行的目录
                program：执行的程序文件路径
"""


class Config(object):
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_dict = self.load_config()

    def load_config(self) -> dict:
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


def run_grib2micaps(no: int, task_param: dict):

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
    default_config_file_name = 'multi_task_loader.config.xml'
    default_config_file_path = os.path.dirname(__file__) + '/' + default_config_file_name

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Load multi task using python's multiprocess module.""")
    parser.add_argument("-c","--config", help="config file path, defaule is "+default_config_file_path)

    args = parser.parse_args()

    config_file_path = default_config_file_path
    if args.config:
        config_file_path = args.config

    print('load config form ' + config_file_path)
    loader_start_time = datetime.datetime.now()

    config = Config(config_file_path)

    print('Loader start...')
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