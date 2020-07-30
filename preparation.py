import pandas as pd
import networkx as nx
import numpy as np
import json
from time import time
from scipy.sparse import csr_matrix
import pickle

# reading files
nodelist = pd.read_csv('./vertices_fs.csv').set_index("id")
edgelist = pd.read_csv('./edges_fs.csv')
# creating graph representation
G = nx.from_edgelist(list(zip(edgelist['id1'],edgelist['id2'])))
# adding nodes that are not in the edgelist
for n in nodelist.index.difference(G.nodes()):
    G.add_node(n)

# creating conversion dictionaries and adjacency matrix
A = nx.adj_matrix(G)
indexmap = {n:i for i,n in enumerate(G.nodes())}
indexmap_back = {i:n for n,i in indexmap.items()}
seed = np.array(nodelist.index[nodelist['month']==1].map(indexmap))

# saving as binary
with open('adjacency.pickle', 'wb') as f:
   pickle.dump([A,indexmap,indexmap_back,seed], f)

edgelist["i"] = edgelist["id1"].map(indexmap)
edgelist["j"] = edgelist["id2"].map(indexmap)

edgelist[["i","j"]].to_csv("R_version/R_adj.csv",index=False,header=True)
np.savetxt(
    "R_version/R_seed.csv.gz",
    seed,
    fmt="%u",
    delimiter=","
)

#print("Number of nodes:", len(G.nodes()))
