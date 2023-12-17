import traci

from trafficSignal import TrafficSignal


class Simulation:
    """
    get the part from sumo env,about reward,state etc.
    """

    def __init__(self, args, sumo_cmd, epochs):

        super(Simulation, self).__init__()

        self.ts_ids_state_veh_spd = None
        self.ts_ids_actions = None
        self.ts_ids_state_veh_num = None
        self.ts_ids_state_veh_acc = None
        self.epochs = epochs
        self.sim_start_time = 0
        self.sim_end_time = 0
        self.total_step = 0
        self.counter = 0
        self.start_time = 0
        self._sumo_cmd = sumo_cmd
        self.ts_ids = []

    def run(self):
        traci.start(self._sumo_cmd)  # 执行sumo命令准备开始仿真
        self._init_param()  # 执行所有需要初始化的地方
        while traci.simulation.getTime() < 3600:
            for i, ts in enumerate(self.ts_ids):
                self.traffic_signals[ts].intersection_calculate()  # 计算step以后交叉口的状态等等
            self._simulation()
        traci.close()

    @staticmethod
    def _simulation():
        traci.simulationStep()

    def _init_param(self):
        self.sim_start_time = traci.simulation.getTime()
        self._init_env_light()

    def _init_env_light(self):
        self.ts_ids = list(traci.trafficlight.getIDList())
        self.traffic_signals = {
            ts: TrafficSignal(
                ts_id=ts,
            ) for i, ts in enumerate(self.ts_ids)
        }
