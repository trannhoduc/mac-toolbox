import random
import simpy

TIME_GEN = 0

class Node:
    NextID = 0  # ID of next Node object to be created
    MsgsSent = 0
    MsgsGenerated = 0  # New class variable to track total messages generated
    TransmittingNodes = []  # Track nodes attempting to transmit in the current slot

    def __init__(self, env, p):
        self.env = env
        self.MyID = Node.NextID
        Node.NextID += 1
        self.P = p

    def run(self):
        while True:
            # Start of the slot: decide whether to transmit
            if random.random() < self.P:
                Node.MsgsGenerated += 1  # Increment total messages generated
                Node.TransmittingNodes.append(self.MyID)  # Add this node to the transmission list

            # End of the slot: handle transmission results
            yield self.env.timeout(1.0)  # Wait for the slot to end

            if len(Node.TransmittingNodes) == 1:
                # If exactly one node transmits, the message is successfully sent
                Node.MsgsSent += 1

            # Clear the list of transmitting nodes for the next slot
            if self.MyID == 0:  # Only the first node clears the list
                Node.TransmittingNodes = []

def run_simulation(N=20, P=0.2, MaxSimtime=10000.0):
    # Reset class variables
    Node.NextID = 0
    Node.MsgsSent = 0
    Node.MsgsGenerated = 0
    Node.TransmittingNodes = []

    # Create simulation environment
    env = simpy.Environment()

    # Create and activate nodes
    nodes = [Node(env, P) for _ in range(N)]
    for node in nodes:
        env.process(node.run())

    # Run simulation
    env.run(until=MaxSimtime)

    # Print results
    print(f"\nSimulation Results:")
    print(f"  Nodes: {N}")
    print(f"  Transmission Prob (P): {P}")
    print(f"  Total Msgs Generated: {Node.MsgsGenerated}")
    print(f"  Total Msgs Sent: {Node.MsgsSent}")
    print(f"  Mean Throughput: {Node.MsgsSent / MaxSimtime:.4f}")
    print(f"  Message Success Rate: {Node.MsgsSent / Node.MsgsGenerated * 100:.2f}%\n")


if __name__ == '__main__':
    # Example usage
    run_simulation(N=10, P=0.2, MaxSimtime=100000.0)
