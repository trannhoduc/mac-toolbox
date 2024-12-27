import random
import simpy
import matplotlib.pyplot as plt
import numpy as np

class Node:
    def __init__(self, env, p):
        self.env = env
        self.MyID = Node.NextID
        Node.NextID += 1
        self.P = p
        self.transmitting = False
        self.last_generated_time = None

    def run(self):
        while True:
            # Wait for the next time slot
            yield self.env.timeout(1.0)

            # Decide whether to transmit in this slot
            if random.random() < self.P:
                Node.MsgsGenerated += 1  # Increment total messages generated
                self.transmitting = True
                self.last_generated_time = self.env.now  # Track the generation time of this message

            else:
                self.transmitting = False


def slotted_aloha(env, nodes):
    """Simulate slotted ALOHA protocol."""
    while True:
        # Start of the time slot
        yield env.timeout(1.0)

        # Count the number of nodes attempting to transmit in this slot
        transmitting_nodes = [node for node in nodes if node.transmitting]

        if len(transmitting_nodes) == 1:
            # If exactly one node transmits, the message is successfully sent
            node_sent = transmitting_nodes[0]
            #if node_sent.last_generated_time is not None:
            Node.MsgsSent += 1
            Node.AoL.append(min(env.now - node_sent.last_generated_time, Node.AoL[-1] + 1))
        else:
            Node.AoL.append(Node.AoL[-1] + 1)  # AoL increments if no new message is received

        '''
        if Received_msg[Node.Slots] == True:
            Node.AoL.append(min(env.now - node_sent.last_generated_time, Node.AoL[-1] + 1))
        else:
            Node.AoL.append(Node.AoL[-1] + 1)
        '''

        # Increment total slots
        Node.Slots += 1


def run_simulation(N=20, P=0.2, MaxSimtime=10000.0):
    # Reset class variables
    Node.NextID = 0
    Node.MsgsSent = 0
    Node.MsgsGenerated = 0
    Node.Slots = 0
    Node.AoL = [0]
    #Node.ReceivedMsg = [False] * MaxSimtime

    # Create simulation environment
    env = simpy.Environment()

    # Create and activate nodes
    nodes = [Node(env, P) for _ in range(N)]
    for node in nodes:
        env.process(node.run())

    # Start slotted ALOHA process
    env.process(slotted_aloha(env, nodes))

    # Run simulation
    env.run(until=MaxSimtime)

    # Print results
    print(f"\nSimulation Results:")
    print(f"  Nodes: {N}")
    print(f"  Transmission Prob (P): {P}")
    print(f"  Total Msgs Generated: {Node.MsgsGenerated}")
    print(f"  Total Msgs Sent: {Node.MsgsSent}")
    print(f"  Mean Throughput: {Node.MsgsSent/Node.Slots:.4f}")
    print(f"  Message Success Rate: {Node.MsgsSent/Node.MsgsGenerated*100:.2f}%")
    print('\n')

    plot_aoi_vs_time(Node.AoL, np.arange(len(Node.AoL)))

def plot_aoi_vs_time(AoI, time):
    plt.plot(time, AoI, ls='-')
    plt.xlabel('Time Slot')
    plt.ylabel('Age of Information (AoI)')
    plt.title('AoI vs. Time')
    plt.grid()
    plt.show()


if __name__ == '__main__':
    # Example usage
    run_simulation(N=10, P=0.01, MaxSimtime=100.0)
