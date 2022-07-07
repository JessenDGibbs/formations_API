#Algorithm 2: Transform
import networkx as nx
from triang_ST_cip import new_G
from triang_ST_cip import added_edges_triang
from functions import *


pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(new_G, pos, with_labels=True)

final_added_edges =  list(added_edges_triang) + list(added_edges_bicon)
final_added_edges

PTP_G = new_G.copy()
for e in sorted(final_added_edges):
  PTP_G = transform(PTP_G, e)

PTP_G.nodes

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [1.5,-1], "12": [-1,-1.5],
       "13": [0.1,-1], "14": [0.7,-0.8], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(PTP_G, pos, with_labels=True)

is_planar, _ = nx.check_planarity(PTP_G, counterexample=False)
print(is_planar)

nx.is_chordal(PTP_G)