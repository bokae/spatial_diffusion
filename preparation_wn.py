import pandas as pd
import networkx as nx
import numpy as np
import json
from time import time
from scipy.sparse import csr_matrix
import pickle

'''
# preparation
'''

nodelist = pd.read_csv('/home/bokanyie/spatial_diffusion/whole_network/nodes_from_edgelist_unique_w_month.csv',header=0)
nodelist.drop(columns=["id","day"])

from scipy.sparse import csr_matrix

# # creating conversion dictionaries and adjacency matrix
print("Starting to read edgelist...")
A = csr_matrix(pd.read_csv("whole_network/edgelist_reindexed.csv",header=None).values)
print("Done.")
print("starting to create helper variables...")
indexmap = {n:i for i,n in pd.read_csv('whole_network/nodes_from_edgelist_unique_w_month_trunc.csv',header=None,index=0).to_dict(orient='index').items()}
indexmap_back = {i:n for n,i in indexmap.items()}
seed = np.array(nodelist["index"][nodelist['month']==1])
print("Done.")

# # saving as binary
# with open('adjacency_wn.pickle', 'wb') as f:
#     pickle.dump([A,indexmap,indexmap_back,seed], f)