from collections import deque
from scipy.stats import planck, poisson
import numpy as np
import simpy

NUM_STATIONS = 4
NUM_REPLICATIONS = 3
TRANSIENT_TIME = 25
TERMINATE_TIME = 10000
STEADY_STATE_TIME = TERMINATE_TIME - TRANSIENT_TIME

class Arrival:
    def __init__(self, name, time):
        self.name = name
        self.time = time

class Frame:
    def __init__(self, start, end, frame_time):
        self.start = start
        self.end = end
        self.frame_time = frame_time
        self.retry = False

    def __repr__(self):
        return f"Frame: start={self.start}, end={self.end}, frame_time={self.frame_time}"

class Station:
    frames_in_transmit = {}

    def __init__(self, env, name, exponential_mean, poisson_mean):
        self.env = env
        self.name = name
        self.exponential_mean = exponential_mean
        self.poisson_mean = poisson_mean
        self.server = simpy.Resource(self.env, capacity=1)
        self.arrivals = deque()
        self.initial_reset_completed = False
        self.n = 0
        self.last_event = 0
        self.nt = 0
        self.st = 0
        self.T = 0
        self.num_retries = 0
        self.num_initial_transmits = 0
        self.mean_retries = 0
        self.busy_time = 0
        self.steady_state_time = 0
        self.U = 0
        self.env.process(self.arrive())

    def generate_report(self):
        self.steady_state_time = self.env.now - TRANSIENT_TIME
        if self.nt > 0:
            self.T = float(self.st) / self.nt
        if self.num_initial_transmits > 0:
            self.mean_retries = float(self.num_retries) / self.num_initial_transmits
        self.U = float(self.busy_time) / self.steady_state_time
        print(f"{self.name} Mean transmit time={self.T}, Mean retries={self.mean_retries}, Utilization={self.U * 100:.2f}%")

    def reset_statistical_counters(self):
        self.nt = 0
        self.st = 0
        self.num_retries = 0
        self.num_initial_transmits = 0
        self.busy_time = 0

    def generate_frame_time(self):
        while True:
            R = planck.rvs(self.exponential_mean, size=1)
            if R[0] > 0:
                return R[0]

    def create_frame(self, frame_time):
        start = self.env.now
        end = self.env.now + frame_time
        return Frame(start, end, frame_time)

    def add_frame_in_transmit(self, frame, frame_id):
        Station.frames_in_transmit[frame_id] = frame

    def remove_frame_in_transmit(self, frame_id):
        return Station.frames_in_transmit.pop(frame_id, None)

    def check_collision(self, frame, frame_id):
        has_collision = False
        for key, other_frame in Station.frames_in_transmit.items():
            if key != frame_id and (other_frame.end > frame.start) and (other_frame.start < frame.end):
                has_collision = True
                other_frame.retry = True
        if has_collision:
            frame.retry = True

    def wait(self):
        mean = 0.0025
        retry_time = planck.rvs(mean, size=1)[0]
        yield self.env.timeout(retry_time)

    def transmit(self, name):
        self.num_initial_transmits += 1
        success = False
        frame_time = self.generate_frame_time()

        while not success:
            frame = self.create_frame(frame_time)
            frame_id = (self.name, name)
            self.add_frame_in_transmit(frame, frame_id)
            transmit_time = self.env.now
            yield self.env.timeout(frame.frame_time)
            self.check_collision(frame, frame_id)
            self.remove_frame_in_transmit(frame_id)

            if frame.retry:
                self.num_retries += 1
                yield self.env.process(self.wait())
            else:
                self.busy_time += self.env.now - transmit_time
                success = True

    def wait_for_service(self, name):
        arrival = Arrival(name, self.env.now)
        self.arrivals.append(arrival)
        self.last_event = self.env.now
        self.n += 1

        with self.server.request() as req:
            yield req
            arrival = self.arrivals.popleft()
            yield self.env.process(self.transmit(name))
            self.nt += 1
            self.st += self.env.now - arrival.time
            self.n -= 1

            if not self.initial_reset_completed and self.env.now >= TRANSIENT_TIME:
                self.reset_statistical_counters()
                self.initial_reset_completed = True

    def arrive(self):
        i = 0
        while True:
            inter_t = poisson.rvs(self.poisson_mean, size=1)[0]
            yield self.env.timeout(inter_t)
            self.env.process(self.wait_for_service(f'Frame {i}'))
            i += 1

def generate_report_single_replication(mean_transmit_times, mean_num_retries, channel_utilizations, stations):
    total_st, total_nt, total_retries, total_initial_transmits, total_busy_time = 0, 0, 0, 0, 0

    for station in stations:
        total_st += station.st
        total_nt += station.nt
        total_retries += station.num_retries
        total_initial_transmits += station.num_initial_transmits
        total_busy_time += station.busy_time

    mean_t = float(total_st) / total_nt if total_nt > 0 else 0
    mean_r = float(total_retries) / total_initial_transmits
    mean_U = float(total_busy_time) / STEADY_STATE_TIME

    mean_transmit_times.append(mean_t)
    mean_num_retries.append(mean_r)
    channel_utilizations.append(mean_U)

    print("Report for the whole system (all stations):")
    print(f"Mean transmit time={mean_t}, Mean number retries={mean_r}, Channel utilization={mean_U * 100:.2f}%")

def generate_report_all_replications(mean_transmit_times, mean_num_retries, channel_utilizations):
    mean_t = np.mean(mean_transmit_times)
    mean_r = np.mean(mean_num_retries)
    mean_U = np.mean(channel_utilizations)

    print("-----------------------")
    print("Report over all replications: (means are over all replications)")
    print(f"Mean transmit time={mean_t}, Mean number retries={mean_r}, Channel utilization={mean_U * 100:.2f}%")

if __name__ == '__main__':
    mean_transmit_times = []
    mean_num_retries = []
    channel_utilizations = []

    for r in range(NUM_REPLICATIONS):
        print("-----------------------")
        print(f"Replication {r + 1}")
        env = simpy.Environment()
        exponential_mean = 0.25
        poisson_mean = 10
        stations = [Station(env, f'Station {i}', exponential_mean, poisson_mean) for i in range(NUM_STATIONS)]
        env.run(until=TERMINATE_TIME)
        print("Report for each Station:")
        for station in stations:
            station.generate_report()
        generate_report_single_replication(mean_transmit_times, mean_num_retries, channel_utilizations, stations)

    generate_report_all_replications(mean_transmit_times, mean_num_retries, channel_utilizations)