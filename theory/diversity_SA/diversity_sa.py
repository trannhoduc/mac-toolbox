import math
import numpy as np
import matplotlib.pyplot as plt

class FrequentDiversity:
    def __init__(self, l, k, G):
        """Initialize the class."""
        self.l = l
        self.k = k
        self.G = G

    def binomial_coefficient(self, n, k):
        """Calculate the binomial coefficient (n choose k)."""
        if k > n or k < 0:
            return 0
        return math.comb(n, k)

    def calculate_Ps_full_formula_replacement(self, l=8, k=1, G=0.8):
        """Calculate P_s (probability message is sent successfully) using the full given formula, including k."""
        l = l or self.l
        k = k or self.k
        G = G or self.G

        Ps = 0  # Initialize P_s

        for m in range(1, l + 1):  # Outer summation over m
            # Calculate the inner summation over v
            inner_sum = 0
            for v in range(0, l - m + 1):
                coefficient = (-1)**v * self.binomial_coefficient(l - m, v)
                inner_sum += coefficient * np.exp(-G * l * (1 - (1 - (m + v) / l)**k))
            
            # Calculate the remaining terms of the formula
            term_1 = 1 - (1 - m / l)**k
            binomial_term = self.binomial_coefficient(l, m)
            
            # Update P_s with the current term
            Ps += term_1 * binomial_term * inner_sum

        return Ps

    def plot_throughput_vs_activity_factor_replacement(self, l=8, G=0.8):
        """
        Plot throughput (S) vs activity factor (Ra) (with replacement).
        - Plot 4 line with k = 1,2,3,4
        - G is the arrival rate parameter
        - L is the total number of channels
        - The function plot by calculating S and Ra by varying G, and k. 
        Additionally, when G rise over a specific value, the throughput will decrease. 
        However, plot by varying S is more difficult when calculating Ps and Ra is more toughful
        """
        l = l or self.l
        G = G or self.G

        G_values = np.linspace(0, G, 50)  # Generate G values for the plot
        for k in range(1, 5):  # Loop over k values
            # Precompute P_s values
            Ps_values = [self.calculate_Ps_full_formula_replacement(l, k, g) for g in G_values]


            # Calculate Throughput (S) and Activity Factor (Ra)
            S = [G_values[i] * Ps_values[i] for i in range(len(G_values))]
            Ra = [1 / Ps_values[i] if Ps_values[i] != 0 else 0 for i in range(len(G_values))]

            # Plot throughput vs activity factor
            plt.plot(S, Ra, label=f'k={k}')

        # Add plot labels and legend
        plt.ylabel('Activity Factor (Ra)')
        plt.xlabel('Throughput (S)')
        plt.title('Throughput vs Activity Factor')
        plt.legend()
        plt.grid()
        plt.show()

    def plot_throughput_vs_activity_factor_without_replacement(self, G=0.8):
        """
        Plot throughput (S) vs activity factor (Ra) (without replacement).
        - Plot 4 line with k = 1,2,3,4
        - G is the arrival rate parameter
        - L is the total number of channels
        - The function plot by calculating S and Ra by varying G, and k. 
        Additionally, when G rise over a specific value, the throughput will decrease. 
        However, plot by varying S is more difficult when calculating Ps and Ra is more toughful
        """
        G = G or self.G
        G_values = np.linspace(0, G, 50)  # Generate G values for the plot
        for k in range(1, 5):  # Loop over k values
            # Precompute P_s values
            Ps_values = [1 - (1 - np.exp(-k * g)) ** k for g in G_values]

            # Calculate Throughput (S) and Activity Factor (Ra)
            S = [G_values[i] * Ps_values[i] for i in range(len(G_values))]
            Ra = [1 / Ps_values[i] if Ps_values[i] != 0 else 0 for i in range(len(G_values))]

            # Plot throughput vs activity factor
            plt.plot(S, Ra, label=f'k={k}')

        # Add plot labels and legend
        plt.ylabel('Activity Factor (Ra)')
        plt.xlabel('Throughput (S)')
        plt.title('Throughput vs Activity Factor')
        plt.legend()
        plt.grid()
        plt.show()

    def plot_throughput_vs_activity_factor_without_replacement_short(self, Ra=1.8):
        '''
        Plot throughput (S) vs activity factor (Ra) (without replacement).
        In this version, we use the simplified formula of realationship between Ra and S.
        '''
        Ra = np.linspace(1, 1.8, 100)
        for k in range(1, 5):
            S = - (1 / (k * Ra)) * np.log(1 - (1 - 1 / Ra) ** (1/k))
            plt.plot(S, Ra, label=f'k={k}')

        # Add plot labels and legend
        plt.ylabel('Activity Factor (Ra)')
        plt.xlabel('Throughput (S)')
        plt.title('Throughput vs Activity Factor')
        plt.legend()
        plt.grid()
        plt.show()

    def plot_beta_vs_Smax_replacement(self, G=0.8, l=16):
        """
        Plot maximum throughput (Smax) vs beta (maximum probability of >= n times fail transmission ).
        - Plot beta vs Smax by varying G
        - The function plot by calculating Smax and beta by varying G
        """
        l = l or self.l
        G = G or self.G

        G_values = np.linspace(0, G, 100)  # Generate beta values
        for n in range(1, 3):
            for k in range(1, 5):
                Ps_values = [self.calculate_Ps_full_formula_replacement(l, k, g) for g in G_values]
                S = [G_values[i] * Ps_values[i] for i in range(len(G_values))]
                beta = [(1 - Ps_values[i])**n for i in range(len(G_values))]

                # Plot beta vs Smax
                if n == 1:
                    plt.plot(beta, S, label=f'n={n}, k={k}', linestyle='--')
                else:
                    plt.plot(beta, S, label=f'n={n}, k={k}')

        # Plot beta vs Smax
        plt.xlabel('Beta')
        plt.xlim(0, 0.1)
        plt.ylabel('Smax')
        plt.legend()
        plt.title('Beta vs Smax')
        plt.grid()
        plt.show()

    def plot_beta_vs_Smax_without_replacement(self):
        """
        Plot maximum throughput (Smax) vs beta (maximum probability of >= n times fail transmission).
        - Plot beta vs Smax by varying G
        - The function plot by calculating Smax and beta by varying G
        """

        beta = np.linspace(0, 0.1, 100)

        for n in range(1, 3):
            for k in range(1, 5):
                Ps_values = [(1 - b ** (1/n)) for b in beta]
                S = [-(Ps / k) * np.log(1 - (1 - Ps) ** (1/k)) for Ps in Ps_values]

                # Plot beta vs Smax
                if n == 1:
                    plt.plot(beta, S, label=f'n={n}, k={k}', linestyle='--')
                else:
                    plt.plot(beta, S, label=f'n={n}, k={k}')

        # Plot beta vs Smax
        plt.xlabel('Beta')
        plt.xlim(0, 0.1)
        plt.ylabel('Smax')
        plt.legend()
        plt.title('Beta vs Smax')
        plt.grid()
        plt.show()

class TimeDiversity:
    def __init__(self, l, k, G):
        """Initialize the class."""
        self.l = l
        self.k = k
        self.G = G

    def binomial_coefficient(self, n, k):
        """Calculate the binomial coefficient (n choose k)."""
        if k > n or k < 0:
            return 0
        return math.comb(n, k)

    def calculate_Ps_full_formula_replacement(self, l=8, k=1, G=0.8):
        """Calculate P_s (probability message is sent successfully) using the full given formula, including k."""
        l = l or self.l
        k = k or self.k
        G = G or self.G

        Ps = 0  # Initialize P_s

        for m in range(1, l + 1):  # Outer summation over m
            # Calculate the inner summation over v
            inner_sum = 0
            for v in range(0, l - m + 1):
                coefficient = (-1)**v * self.binomial_coefficient(l - m, v)
                inner_sum += coefficient * np.exp(-G * l * (1 - (1 - (m + v) / l)**k))
            
            # Calculate the remaining terms of the formula
            term_1 = 1 - (1 - m / l)**k
            binomial_term = self.binomial_coefficient(l, m)
            
            # Update P_s with the current term
            Ps += term_1 * binomial_term * inner_sum

        return Ps

    def plot_throughput_vs_activity_factor_replacement(self, l=8, G=0.8):
        """
        Plot throughput (S) vs activity factor (Ra) (with replacement).
        - Plot 4 line with k = 1,2,3,4
        - G is the arrival rate parameter
        - L is the total number of channels
        - The function plot by calculating S and Ra by varying G, and k. 
        Additionally, when G rise over a specific value, the throughput will decrease. 
        However, plot by varying S is more difficult when calculating Ps and Ra is more toughful
        """
        l = l or self.l
        G = G or self.G

        G_values = np.linspace

if __name__ == "__main__":
    # Example Inputs
    l = 8  # Total number of channels
    k = 1   # Number of copies of the message sent
    G = 0.8 # Arrival rate parameter

    # Calculate P_s using the full formula
    agent = FrequentDiversity(l, k, G)
    agent.plot_beta_vs_Smax_replacement()
    agent.plot_beta_vs_Smax_without_replacement()
