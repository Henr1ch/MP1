import copy
import math
from collections import namedtuple

import numpy as np
import torch
import torch.nn.functional as F
import traci
from torch.distributions import Categorical
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
from utils import return_args

args = return_args()


class TrafficSignal:
    def __init__(self, ts_id):
        # <<仿真过程中需要用到的一些参数
        # reward
        self.next_phase_id = None
        self.phases_run_time = 0
        self.incoming_edges = None  # 进口方向
        self.training_step = 0
        self.action = 0

        self.fixed_time = 0  # 控制信号同步
        self.id = ts_id
        self.phase_id = 0
        self.lanes = traci.trafficlight.getControlledLanes(self.id)
        self.links = traci.trafficlight.getControlledLinks(self.id)
        self.incoming_lanes = list(dict.fromkeys(traci.trafficlight.getControlledLanes(self.id)))  # 和phase的state顺序是对应的
        self.outgoing_lanes = [link[0][1] for link in traci.trafficlight.getControlledLinks(self.id) if link]
        self.outgoing_lanes = list(set(self.outgoing_lanes))
        # lane是所有进口车道
        self.phases = traci.trafficlight.getAllProgramLogics(self.id)[0].phases

    def _set_green_phase(self, action_number):
        traci.trafficlight.setPhase(self.id, action_number)

    def intersection_calculate(self):
        if self.phases_run_time % args.min_green_duration != 0:
            self.phases_run_time += 1
            self._set_green_phase(self.phase_id)
        else:
            max_pressure = -math.inf
            for i, phase in enumerate(self.phases):
                if i % 2 == 0:
                    pressure = self.get_pressure_for_phase(phase.state)
                    if pressure > max_pressure:
                        max_pressure = pressure
                        self.next_phase_id = i
            if self.next_phase_id != self.phase_id:
                self.phases_run_time = 0
            self.phase_id = self.next_phase_id
            self._set_green_phase(self.phase_id)

    def intersection_calculate_2(self):
        if self.phases_run_time % args.min_green_duration != 0:
            self.phases_run_time += 1
            self._set_green_phase(self.phase_id)
        else:
            current_pressure = self.get_pressure_for_phase(self.phases[self.phase_id].state)
            if self.phase_id == len(self.phases) - 2:
                self.next_phase_id = 0
            else:
                self.next_phase_id = self.phase_id + 2
            next_phase_pressure = self.get_pressure_for_phase(self.phases[self.next_phase_id].state)
            if current_pressure <= next_phase_pressure and self.phase_id == len(self.phases) - 2:
                self.next_phase_id = 0
            elif current_pressure <= next_phase_pressure:
                self.next_phase_id = self.phase_id + 2
            elif current_pressure > next_phase_pressure:
                self.next_phase_id = self.phase_id
            if self.next_phase_id != self.phase_id:
                self.phases_run_time = 0
            self.phase_id = self.next_phase_id
            self._set_green_phase(self.phase_id)
            print(self.phase_id)

    def get_pressure_for_phase(self, phase_state):
        pressure = 0
        indices = [i for i, char in enumerate(phase_state) if char == 'G']
        for j in indices:
            pressure += traci.lane.getLastStepHaltingNumber(self.links[j][0][0])
            pressure -= traci.lane.getLastStepHaltingNumber(self.links[j][0][1])
        return pressure
