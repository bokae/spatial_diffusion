import numpy as np
import json
import pickle
import sys
from scipy.optimize import curve_fit


class SI:
    def __init__(self, **conf):

        # reading params from the config conf, otherwise set to default
        # parameter 'p' of the Bass model
        self.p = conf.get("p", 0.000104)
        # parameter 'q' of the Bass model
        self.q = conf.get("q", 0.12)
        # number of timesteps
        self.stop = conf.get("stop", 129)
        # correcting the threshold
        self.high = conf.get("high", 0)
        self.low = conf.get("low", 0)
        # total number of runs with the above parameter settings
        self.num_runs = conf.get("num_runs", 1)

        # reading in byte-saved variables created by preferences.py that are the same for each run
        with open('adjacency.pickle', 'rb') as f:
            # A is the adjacency matrix
            # indexmap maps user_ids to the row indices of A
            # indexmap_back maps row indices of A to user_ids
            # seed is a boolean vector of the initial infected nodes
            self.A, self.indexmap, self.indexmap_back, self.seed = pickle.load(f)

        # creating the necessary variables, setting the initial infected nodes
        self.restart()

    def restart(self):
        # init new simulation
        self.time_counter=1

        # creating infected and susceptible lists
        self.infected = np.zeros(self.A.shape[0], dtype=bool)
        # initial infection
        self.infected[self.seed] = True
        # initial susceptibles, aka everybody who's not infected
        self.susceptible = ~self.infected

        # storing the infection time for the nodes, setting infected nodes times to 1
        self.time_infected = np.array(self.infected, dtype=int)

        # storing number of infected neighbors for nodes
        self.node_neighborhood_num_infected = np.matrix(np.zeros_like(self.infected, dtype=float))
        # storing total number of neighbors
        self.node_neighborhood_num_neighbors = self.A.sum(axis=0)
        # adding 1 for isolated nodes to avoid division by 0
        self.node_neighborhood_num_neighbors[(self.node_neighborhood_num_neighbors == 0)[0]] = 1
        # counting number of infected neighbors for initial infection
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
        # increment time counter
        self.time_counter += 1

        # fraction of infected neighbors vs total neighbors
        a = self.node_neighborhood_num_infected/self.node_neighborhood_num_neighbors
        # uniform random number between 0 and 1
        r = np.random.rand(a.shape[1])
        # calculating threshold, comparing random number to threshold
        mask = (r < self.p + self.q*self.transform(a))
        # infect nodes where random number is smaller than the threshold and that are susceptible
        new_infected = np.array(self.susceptible & mask)[0]

        # store infection time for newly infected nodes
        self.time_infected[new_infected] = self.time_counter
        # union of old and new infections
        self.infected = self.infected | new_infected
        # decreasing the susceptibles with the newly infected nodes
        self.susceptible = self.susceptible & (~new_infected)
        # incrementing the counters in the array storing the number of infected neighbors
        self.node_neighborhood_num_infected += self.A[new_infected].sum(axis=0)

        return new_infected.sum()

    def run_new(self):
        # init simulation, time_counter = 1
        self.restart()
        # stepping time
        for t in range(2, self.stop):
            n = self.step_time()

        # storing results, raw output
        return {
            "time_infected": {str(self.indexmap_back[i]): int(t) for i, t in enumerate(self.time_infected) if t!=0},
            "p": self.p,
            "q": self.q,
            "stop": self.stop,
            "num_nodes": self.A.shape[0],
            "high": self.high,
            "low": self.low
        }

    def run_batch(self):
        # storing results of multiple runs in a dictionary
        o = {}
        # running the simulation multiple times, same parametrization
        for run in range(self.num_runs):
            res = self.run_new()
            o["run_" + str(run).zfill(2)] = res

        return o

    def average_batch(self, o):
        timelines = []

        for r in o:
            node_adoptions = o[r]["time_infected"]

            # getting adoption time histogram
            timeline = np.zeros(self.stop)
            for k in node_adoptions.keys():
                timeline[node_adoptions[k] - 1] += 1
            timelines.append(timeline)

        return {
            "avg_timeline": list(np.array(timelines).mean(axis=0)),
            "p": self.p,
            "q": self.q,
            "stop": self.stop,
            "num_nodes": self.A.shape[0],
            "high": self.high,
            "low": self.low
        }


class DE_fit:
    def __init__(self, avg_output):
        self.t = np.array(range(1,avg_output["stop"]+1))
        self.timeline = avg_output["avg_timeline"]
        self.cum_timeline = np.cumsum(self.timeline)
        self.N = avg_output["num_nodes"]
        self.p = avg_output["p"]
        self.q = avg_output["q"]

    def bass_solution(self, t, P, Q):
        # Bass DE solution
        return self.N * (1-np.exp(-(P+Q)*t))/(1+Q/P*np.exp(-(P+Q)*t))

    def fit(self):
        param, param_cov = curve_fit(self.bass_solution, self.t, self.cum_timeline, p0=[self.p, self.q])
        return param, param_cov

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
