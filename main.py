import os
import time

import matplotlib.pyplot as plt
from tqdm import tqdm
from simulation import Simulation
from utils import sumo_check, return_args

root = os.getcwd()
file_path = root + '\\exam_record\\' + time.strftime("%Y%m%d-%H%M", time.localtime())
static_file_path = file_path + "\\static_file"
if not os.path.exists(static_file_path):
    os.makedirs(static_file_path)
else:
    print("路径已经存在，将继续往下执行")

args = return_args()

if __name__ == '__main__':
    sim_step = []  # 储存仿真总步数的列表，打印输出用
    for epoch in tqdm(range(args.epochs)):
        print("epochs ： ", epoch)
        sumo_cmd = sumo_check(args.gui, args.sumocfg_file_name,
                              static_file_name='{}.xml'.format(epoch),
                              static_file_path=static_file_path)
        simulator = Simulation(sumo_cmd=sumo_cmd, args=args, epochs=epoch)
        simulator.run()
