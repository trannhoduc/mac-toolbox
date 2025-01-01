import numpy as np
import matplotlib.pyplot as plt

def delay(M, P, R):
    '''
    Calculate the average delay in a system with M servers (M/D/1)
    '''
    return M * (2 - P) / (2 * (1 - P))

def plot_delay_vs_M(M, P, R):
    '''
    Plot the average delay as a function of the number of servers M
    '''
    M = np.arange(1, M, 1)
    delays = [delay(m, P, R) for m in M]
    plt.plot(M, delays)
    plt.xlabel('Number of servers M')
    plt.ylabel('Expected Delay')
    #plt.yscale('log')
    plt.title('Expected Delay vs. number of servers M')
    plt.grid()
    plt.legend()
    plt.show()

def plot_delay_vs_P(P, R):
    '''
    Plot the average delay as a function of the utilization P
    '''
    P_values = np.linspace(0, P, 100)  # Generate 100 points for smooth plotting
    P_values = np.delete(P_values, 0)
    
    delays_0 = [delay(5, p, R) for p in P_values]
    delays_1 = [delay(10, p, R) for p in P_values]
    delays_2 = [delay(100, p, R) for p in P_values]
    delays_3 = [delay(1000, p, R) for p in P_values]
    
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
    '''
    Define parameters
    - M: number of servers
    - R: transmission rate
    - lamda: arrival rate
    - mu: service rate
    - P: utilization
    '''
    M = 10
    R = 1
    lamda = 0.1
    mu = 0.2
    P = lamda / mu

    # Plot average delay vs. number of servers M
    plot_delay_vs_M(M, P, R)
    plot_delay_vs_P(1, R)