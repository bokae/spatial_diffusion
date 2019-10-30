import numpy as np
import json
import pickle
import sys


class SI:
    def __init__(self, **conf):
        self.p = conf.get("p", 0.000104)
        self.q = conf.get("q", 0.12)
        self.stop = conf.get("stop", 129)
        self.high = conf.get("high", 0)
        self.low = conf.get("low", 0)
        self.num_runs = conf.get("num_runs", 1)

        with open('adjacency.pickle', 'rb') as f:
            self.A, self.indexmap, self.indexmap_back, self.seed = pickle.load(f)

        self.restart()

    def restart(self):
        # init new simulation
        self.time_counter=1

        # creating infected and susceptible lists
        self.infected = np.zeros(self.A.shape[0], dtype=bool)
        self.infected[self.seed] = True
        self.susceptible = ~self.infected

        # storing the infection time for the nodes, setting infected nodes times to 1
        self.time_infected = np.array(self.infected, dtype=int)

        # storing number of infected neighbors for nodes
        self.node_neighborhood_num_infected = np.matrix(np.zeros_like(self.infected, dtype=float))
        self.node_neighborhood_num_neighbors = self.A.sum(axis=0)
        self.node_neighborhood_num_neighbors[(self.node_neighborhood_num_neighbors == 0)[0]] = 1
        self.node_neighborhood_num_infected += self.A[self.infected].sum(axis=0)

    def transform(self, a):
        """
        Function that is able to correct for neighborhood infection rate.
        """

        x = [0, 0.5, 1]
        y = [1-self.low, 1+self.high, 1-self.low]
        params = np.polyfit(x, y, 2)

        return np.polyval(params, a)*np.array(a)

    def step_time(self):
        # create neighbor fractions, flip coins for infection
        a = self.node_neighborhood_num_infected/self.node_neighborhood_num_neighbors
        r = np.random.rand(a.shape[1])
        mask = (r < self.p + self.q*self.transform(a))
        new_infected = np.array(self.susceptible & mask)[0]

        # update lists, update counters
        self.time_infected[new_infected] = self.time_counter
        self.infected = self.infected | new_infected
        self.susceptible = self.susceptible & (~new_infected)
        self.node_neighborhood_num_infected += self.A[new_infected].sum(axis=0)

        return new_infected.sum()

    def run_new(self):
        self.restart()
        for time_counter in range(2, self.stop):
            self.time_counter = time_counter
            n = self.step_time()

        # storing results
        return {
            "time_infected": {str(self.indexmap_back[i]): int(t) for i, t in enumerate(self.time_infected)},
            "p": self.p,
            "q": self.q,
            "stop": self.stop,
            "num_nodes": self.A.shape[0]
        }


if __name__ == "__main__":

    # reading config from standard input, if None, then values are default
    conf = json.load(sys.stdin)
    # initializing simulation with values from conf
    simulation = SI(**conf)

    # storing results of multiple runs in a dictionary
    output = {}
    # running the simulation multiple times, same parametrization
    for r in range(simulation.num_runs):
        result = simulation.run_new()
        output["run_"+str(r).zfill(2)] = result

    print(json.dumps(output))
