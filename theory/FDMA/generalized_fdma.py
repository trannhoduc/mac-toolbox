import numpy as np
import matplotlib.pyplot as plt

class Generalized_FDMA():
    def __init__(self, M=10, R=1, L=1, Tc=1, lamda=0.5, mu=1):
        self.M = M
        self.R = R
        self.L = L
        self.Tc = Tc
        self.T = self.Tc * self.M
        self.lamda = lamda
        self.mu = mu
        self.P = self.lamda * self.L * self.Tc
    
    def calculate_delay(self, M=None, L=None, P=None):
        # Use default values from instance attributes if parameters are not provided
        M = M if M is not None else self.M
        L = L if L is not None else self.L
        P = P if P is not None else self.P

        '''
        Calculate the average delay in a system with M servers
        '''
        if P >= 1:
            return 0  # Return 0 if utilization is 100% or more to avoid division by zero
        return M * (L - 1 / 2) + ((M * L ** 2) / L) * (P / (2 * (1 - P))) + 1

    
    def plot_delay_vs_M(self, M=None, L=None, P=None):
        '''
        Plot the average delay as a function of the number of servers M
        '''
        M = M if M is not None else self.M
        L = L if L is not None else self.L
        P = P if P is not None else self.P

        M = np.arange(1, M, 1)
        delays = [self.calculate_delay(m, L, P) for m in M]
        plt.plot(M, delays)
        plt.xlabel('Number of servers M')
        plt.ylabel('Expected Delay')
        #plt.yscale('log')
        plt.title('Expected Delay vs. number of servers M')
        plt.grid()
        plt.legend()
        plt.show()

    def plot_delay_vs_P(self, L=None):
        '''
        Plot the average delay as a function of the utilization P
        '''
        L = L if L is not None else self.L

        P = 1 # maximum value
        P_values = np.linspace(0, P, 100)  # Generate 100 points for smooth plotting
        P_values = np.delete(P_values, [0, 99])
        
        delays_0 = [self.calculate_delay(5, L, p) for p in P_values]
        delays_1 = [self.calculate_delay(10, L, p) for p in P_values]
        delays_2 = [self.calculate_delay(100, L, p) for p in P_values]
        delays_3 = [self.calculate_delay(1000, L, p) for p in P_values]
        
        plt.plot(P_values, delays_0, label='M=5')
        plt.plot(P_values, delays_1, label='M=10')
        plt.plot(P_values, delays_2, label='M=100')
        plt.plot(P_values, delays_3, label='M=1000')
        
        plt.xlabel('Throughput S')
        plt.yscale('log')
        plt.ylabel('Expected delay')
        plt.title('FDMA Expected Delay vs. Throughput')
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == '__main__':
    agent = Generalized_FDMA()
    print(agent.calculate_delay())
    agent.plot_delay_vs_P()
    agent.plot_delay_vs_M()