import numpy as np
import simpy
from prettytable import PrettyTable

NUM_NODES = 10  # Number of nodes
SIM_TIME = 10000  # Total simulation time
SLOT_TIME = 1  # Time duration of each slot
LAMBDA = 0.1  # Average arrival rate for Poisson distribution

class Node:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.message_arrival_time = None
        self.retry_time = None
        self.initial_transmissions = 0
        self.retries = 0
        self.total_delay = 0
        self.total_retry_time = 0
        self.total_schedule_time = 0
        self.successful_transmissions = 0
        self.env.process(self.generate_message())

    def generate_message(self):
        while True:
            # Generate message arrival time using Poisson distribution
            inter_arrival_time = np.random.exponential(1 / LAMBDA)
            yield self.env.timeout(inter_arrival_time)
            self.message_arrival_time = self.env.now
            self.initial_transmissions += 1
            yield self.env.process(self.transmit_message())

    def transmit_message(self):
        while True:
            # Wait until the start of the next slot
            wait_time = SLOT_TIME - (self.env.now % SLOT_TIME)
            yield self.env.timeout(wait_time)

            # Assume the time for transmission and waiting for ACK is negligible
            yield self.env.timeout(2 * SLOT_TIME)

            # Attempt to transmit the message
            Channel.attempt_transmission(self)

            if self.message_arrival_time is None:  # Transmission was successful
                self.successful_transmissions += 1
                break
            else:
                # Wait for a random backoff time before retrying
                self.retries += 1
                retry_time = np.random.randint(1, 10) * SLOT_TIME
                self.total_retry_time += retry_time
                self.total_schedule_time += retry_time
                yield self.env.timeout(retry_time)

class Channel:
    slots = {}

    @staticmethod
    def reset():
        Channel.slots = {}

    @staticmethod
    def attempt_transmission(node):
        current_slot = node.env.now

        # Check if any other node is transmitting in this slot
        if current_slot not in Channel.slots:
            Channel.slots[current_slot] = [node]
        else:
            Channel.slots[current_slot].append(node)

        if len(Channel.slots[current_slot]) == 1:
            # Successful transmission
            delay = current_slot - node.message_arrival_time
            node.total_delay += delay
            node.message_arrival_time = None
        else:
            # Collision occurred
            pass  # Do not reset message_arrival_time

# Reporting function
def generate_report(nodes):
    successful_transmissions = 0
    total_transmissions = 0
    total_initial_transmissions = 0
    total_retries = 0
    total_delay = 0
    total_retry_time = 0
    total_schedule_time = 0

    for slot, transmitting_nodes in Channel.slots.items():
        if len(transmitting_nodes) == 1:
            successful_transmissions += 1
        total_transmissions += len(transmitting_nodes)

    for node in nodes:
        total_initial_transmissions += node.initial_transmissions
        total_retries += node.retries
        total_delay += node.total_delay
        total_retry_time += node.total_retry_time
        total_schedule_time += node.total_schedule_time

    throughput = successful_transmissions / (SIM_TIME / SLOT_TIME)
    mean_delay = total_delay / successful_transmissions if successful_transmissions > 0 else 0
    mean_retry_time = total_retry_time / total_retries if total_retries > 0 else 0
    mean_schedule_time = total_schedule_time / total_retries if total_retries > 0 else 0

    table = PrettyTable()
    table.field_names = ["Metric", "Value"]
    table.add_row(["Number of Nodes", NUM_NODES])
    table.add_row(["Lambda (Arrival Rate)", LAMBDA])
    table.add_row(["Simulation Time", SIM_TIME])
    table.add_row(["Initial Transmissions", total_initial_transmissions])
    table.add_row(["Retries", total_retries])
    table.add_row(["Total Transmissions", total_transmissions])
    table.add_row(["Successful Transmissions", successful_transmissions])
    table.add_row(["Throughput (packets/slot)", f"{throughput:.4f}"])
    table.add_row(["Mean Delay (time units)", f"{mean_delay:.4f}"])
    table.add_row(["Mean Retry Time (time units)", f"{mean_retry_time:.4f}"])
    table.add_row(["Average Time Schedule (time units)", f"{mean_schedule_time:.4f}"])

    print("\nSimulation Results:")
    print(table)

if __name__ == '__main__':
    env = simpy.Environment()
    Channel.reset()
    nodes = [Node(env, f"Node {i}") for i in range(NUM_NODES)]
    env.run(until=SIM_TIME)
    generate_report(nodes)
