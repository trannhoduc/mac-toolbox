import numpy as np
import matplotlib.pyplot as plt

class Simplified_FDMA:
    def __init__(self, M=10, R=1, lamda=0.1, mu=0.2):
        self.M = M  # Default number of servers
        self.R = R  # Transmission rate
        self.lamda = lamda  # Arrival rate
        self.mu = mu  # Service rate
        self.P = self.lamda / self.mu  # Utilization

    def calculate_delay(self, M=None, P=None):
        '''
        Calculate the average delay in a system with M servers (M/D/1).
        '''
        M = M if M is not None else self.M
        P = P if P is not None else self.P
        if P >= 1:
            return float('inf')  # Return infinity if utilization is 100% or more
        return M * (2 - P) / (2 * (1 - P))

    def plot_delay_vs_M(self, M=None, P=None):
        '''
        Plot the average delay as a function of the number of servers M.
        '''
        M = M if M is not None else self.M
        P = P if P is not None else self.P

        M_values = np.arange(1, M + 1, 1)  # Ensure it includes up to `M`
        delays = [self.calculate_delay(m, P) for m in M_values]
        plt.plot(M_values, delays, label=f'P={P:.2f}')
        plt.xlabel('Number of servers M')
        plt.ylabel('Expected Delay')
        plt.title('Expected Delay vs. Number of Servers M')
        plt.grid()
        plt.legend()
        plt.show()

    def plot_delay_vs_P(self, P_max=1):
        '''
        Plot the average delay as a function of the utilization P.
        '''
        P_values = np.linspace(0.01, P_max, 100)  # Avoid P=0 to prevent division by zero

        delays_5 = [self.calculate_delay(5, p) for p in P_values]
        delays_10 = [self.calculate_delay(10, p) for p in P_values]
        delays_100 = [self.calculate_delay(100, p) for p in P_values]
        delays_1000 = [self.calculate_delay(1000, p) for p in P_values]

        plt.plot(P_values, delays_5, label='M=5')
        plt.plot(P_values, delays_10, label='M=10')
        plt.plot(P_values, delays_100, label='M=100')
        plt.plot(P_values, delays_1000, label='M=1000')

        plt.xlabel('Utilization P')
        plt.yscale('log')
        plt.ylabel('Expected Delay')
        plt.title('FDMA Expected Delay vs. Utilization')
        plt.legend()
        plt.grid()
        plt.show()


if __name__ == '__main__':
    # Create an instance of the FDMA class
    agent = Simplified_FDMA(M=10, R=1, lamda=0.1, mu=0.2)
    
    # Calculate and print delay with default values
    print(f"Default delay: {agent.calculate_delay()}")

    # Plot delay vs. number of servers
    agent.plot_delay_vs_M()

    # Plot delay vs. utilization
    agent.plot_delay_vs_P(P_max=1)
