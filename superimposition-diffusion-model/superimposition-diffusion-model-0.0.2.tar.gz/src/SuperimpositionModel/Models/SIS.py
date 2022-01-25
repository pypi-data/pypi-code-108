import networkx as nx
from .ModelConfig import ModelConfig
import random
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt

class SIS:
    def __init__(self , graph : nx.Graph ) :
        self._graph = graph
        self._result = {
            "details": [],
            "trends" : {
                "S":[],
                "I":[]
            }
        }
        self._g2 = None
        #############
        self._config = None
        self.beta1 = 0
        self.beta2 = 0
        self.recovery_rate = 0
        self.initial_infected = 0
        self.threshold = 0
        self.m = 0
        self.int_p = 0
        self.int_size = 0
        self.HO_prop = None
        #############
        self.healthy_list = list(self._graph.nodes)
        self.new_infected = set()
        self.infected_list = list()
        self.vertex_set = list(self._graph.nodes)
        self.node_dict = {key: 0 for key in self.vertex_set}
        self.node_association = {key: list() for key in self.vertex_set}
        #############
        # self.HO_condition = lambda n , i , t : i / (n-1) >= t 
        # self.HO_probability = lambda n , i , t : self.beta2
    
    def set_initial_status(self , configuration : ModelConfig):
        
        self._config = configuration.config
        self.beta1 = self._config["beta1"]
        self.beta2 = self._config["beta2"]
        self.recovery_rate = self._config["recovery_prob"]
        self.initial_infected = self._config["initial_infected"]
        self.threshold = self._config["Threshold"]
        self.m = self._config["number_of_groups"]
        self.int_p = self._config["intersection_probability"]
        self.HO_prop = self._config["HO_prapagation_mechanism"]
        self._g2 = { i : {"nodes" : [] , "size":0 , "infected": 0} for i in range(self._config["number_of_groups"])}
        self.int_size = self._config["intersection_size"]

        if self.HO_prop == "Customized":
            self.HO_condition = self._config["HO_condition"] 
            self.HO_probability = self._config["HO_probability"]

        if self._config["HO_node_lists"] == None:
            if self.int_size > 0:
                self.initialize_intersection_graph_k()
            else:
                self.initialize_intersection_graph()
        else:
            self.initialize_fixed_HO_structure(self._config["HO_node_lists"])
        self.apply_random_infection()

    
    def initialize_fixed_HO_structure(self , group_list):
        # self._g2 = { i : {"nodes" : list(set(gr)) , "size":len(gr) , "infected": 0} for i , gr in enumerate(group_list) if len(gr)>=3}
        for i, gr in enumerate(group_list):
            self._g2[i] = {"nodes": list(set(gr)), "size": len(gr), "infected": 0}
            for node in gr:
                self.node_association[node].append(i)


    def initialize_intersection_graph(self):
        for key in self.vertex_set:
            for feature in self._g2.keys():
                if random.uniform(0, 1) < self.int_p:
                    self._g2[feature]["nodes"].append(key)
                    self._g2[feature]["size"]+=1
                    self.node_association[key].append(feature)

    def initialize_intersection_graph_k(self):
        all_nodes = list(self._graph.nodes)
        for feature in self._g2.keys():
            chosen_nodes = random.sample(all_nodes , self.int_size)
            for key in chosen_nodes:
                self._g2[feature]["nodes"].append(key)
                self._g2[feature]["size"]+=1
                self.node_association[key].append(feature)

    def apply_random_infection(self):
        for key in self.vertex_set:
            if random.uniform(0, 1) < self.initial_infected:
                self.infected_list.append(key)
                self.healthy_list.remove(key)
                self.node_dict[key] = 1
                if len(self.node_association[key]) > 0:
                    for feature in self.node_association[key]:
                        self._g2[feature]["infected"]+=1
    
    def propagate(self):
        # pair-wise propagation on g1
        if self.beta1 >0 :
            for u, v in list(self._graph.edges()):
                if self.node_dict[u] == 1 and self.node_dict[v] == 0 and random.uniform(0, 1) < self.beta1:
                    self.new_infected.add(v)
                if self.node_dict[u] == 0 and self.node_dict[v] == 1 and random.uniform(0, 1) < self.beta1:
                    self.new_infected.add(u)

        # Higher-order propagation on g2
        if self.beta2>0:
            if self.HO_prop == "ThresholdClique":
                self.threshold_clique()
            elif self.HO_prop == "Clique":
                self.clique_contagion()
            elif self.HO_prop == "Triangle":
                self.triangle_contagion()
            elif self.HO_prop == "Customized":
                self.customized_HO_propagation()

    def customized_HO_propagation(self):
        for feature in self._g2.keys():
            if self._g2[feature]["size"]>2:
                for node in self._g2[feature]["nodes"]:
                    if self.node_dict[node] == 0 and self.HO_condition(self._g2[feature]["size"] , self._g2[feature]["infected"]) and random.uniform(0, 1) < self.HO_probability(self._g2[feature]["size"] , self._g2[feature]["infected"]):
                        self.new_infected.add(node)
        

    def threshold_clique(self):
        if self.beta2> 0:
            for feature in self._g2.keys():
                if self._g2[feature]["size"]>2 and self._g2[feature]["infected"] / (self._g2[feature]["size"])>=self.threshold:
                #   prob = self.g2[feature]["infected"]*self.p2 / (self.g2[feature]["size"]-1)
                    for node in self._g2[feature]["nodes"]:
                        if self.node_dict[node] == 0 and random.uniform(0, 1) < self.beta2:
                            self.new_infected.add(node)

    def clique_contagion(self):
        if self.beta2> 0:
            for feature in self._g2.keys():
                if self._g2[feature]["size"]>2:
                    prob = self._g2[feature]["infected"]*self.beta2 / (self._g2[feature]["size"]-1)
                    for node in self._g2[feature]["nodes"]:
                        if self.node_dict[node] == 0 and random.uniform(0, 1) < prob:
                            self.new_infected.add(node)

    def triangle_contagion(self):
        if self.beta2 > 0:
            for group in self._g2.keys():
                if self._g2[group]["size"]>=3:
                    triangles = [(node[0] , node[1] , node[2])for node in combinations(list(self._g2[group]["nodes"]),3)]
                    for triangle in triangles:
                        n1, n2, n3 = triangle
                        if self.node_dict[n1]==1:
                            if self.node_dict[n2]==1:
                                if self.node_dict[n3]==0:
                                    #infect n3 with probability beta2
                                    if (random.random() <= self.beta2): 
                                        self.new_infected.add(n3)
                            else:
                                if self.node_dict[n3]==1:
                                    #infect n2 with probability beta2
                                    if (random.random() <= self.beta2): 
                                        self.new_infected.add(n2)
                        else:
                            if self.node_dict[n2]==1 and self.node_dict[n3] == 1:
                                #infect n1 with probability beta2
                                if (random.random() <= self.beta2): 
                                    self.new_infected.add(n1)
    
    def update_new_infected(self):
        new_infected_set = set(self.new_infected)
        for node in list(new_infected_set):
            self.infected_list.append(node)
            self.healthy_list.remove(node)
            self.node_dict[node] = 1
            if len(self.node_association[node]) > 0:
                for feature in self.node_association[node]:
                    self._g2[feature]["infected"]+=1
        self.new_infected = set()

    def heal_by_chance(self):
        for node in self.infected_list:
            if random.uniform(0, 1) < self.recovery_rate:
                self.infected_list.remove(node)
                self.healthy_list.append(node)
                self.node_dict[node] = 0
                if len(self.node_association[node]) > 0:
                    for feature in self.node_association[node]:
                        self._g2[feature]["infected"]-=1
    
    def run(self, numiters):
        """
            run simulation

            step1:
                load dataset of cliques
            step2:
                get the vertex node_dict
            step3:
                choose random vertex with prob p

            while():
                step4:
                    for each clique propagate infection
        """
        time = 1
        while True:
            state = {
                "nodes" : {},
                "num_infected": 0,
                "num_susceptible":0,
                "num_recovered":0,
                "iteration": 0
            }
            num_of_infected = len(self.infected_list)

            state["num_infected"] = num_of_infected
            state["num_susceptible"] = self._graph.number_of_nodes() - num_of_infected
            state["nodes"] = self.node_dict.copy()
            state["iteration"] = time

            self._result["details"].append(state)
            self._result["trends"]["I"].append(len(self.infected_list)/self._graph.number_of_nodes())
            self._result["trends"]["S"].append(len(self.healthy_list)/self._graph.number_of_nodes())

            # self.phro_list.append(num_of_infected)
            if num_of_infected == 0 or time == numiters:
                break
            self.propagate()
            self.heal_by_chance()
            self.update_new_infected()
            time = time + 1
            self._result
        return self._result

    def draw(self, obj):
        df = pd.DataFrame.from_dict(obj["trends"]).reset_index(drop=True)
        plt.style.use('seaborn-darkgrid')
        line = df.plot(kind= "line" , figsize=(10,7))
        line.set_xlabel("iteration")
        line.set_ylabel("\u03C1")