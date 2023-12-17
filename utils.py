import argparse
import os
import random
import sys

import numpy as np
import torch
from sumolib import checkBinary


def sumo_check(gui, sim_file_name, static_file_path,  static_file_name="111.xml"):  # 将最后一位设置为原始参数的路网数据
    """
    check whether sumo is in env or not
    :param static_file_path:
    :param static_file_name:
    :param stop_file_name:
    :param gui:bool,whether to use sumo gui or not
    :param sim_file_name:
    :param queue_file_name:
    :param queue_file_path:
    :param stop_file_path:
    :return:sumo_cmd
    """
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    if gui:
        sumoBinary = checkBinary('sumo-gui')
    else:
        sumoBinary = checkBinary('sumo')

    sumo_cmd = [sumoBinary, "--statistic-output", os.path.join(static_file_path, static_file_name),
                            "-c", os.path.join('net\\hangzhou', sim_file_name),
                            "--no-step-log", "true",
                            "-W", "true",
                            "--duration-log.statistics", "true"
                ]

    return sumo_cmd


def return_args():  # 返回训练中需要的参数
    parser = argparse.ArgumentParser("Hyperparameter Setting for PPO-discrete")

    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument("--gui", type=bool, default=False, help=" 是否使用GUI界面 ")
    parser.add_argument("--min_green_duration", type=int, default=10, help=" 绿灯最小时长 ")
    parser.add_argument("--yellow_duration", type=int, default=3, help=" 黄灯时长 ")
    parser.add_argument("--sumocfg_file_name", type=str, default="HZ.sumocfg", help=" 使用的仿真文件 ")
    parser.add_argument("--epochs", type=int, default=100, help=" epochs ")
    parser.add_argument("--episodes", type=int, default=10, help=" 总训练次数 ")
    parser.add_argument("--file_path", type=str, default="error", help=" 仿真文件路径 ")

    args = parser.parse_args()

    set_seed_everywhere(args.seed)

    return args


def set_seed_everywhere(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
