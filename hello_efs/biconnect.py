from functions import *
import networkx as nx
from test_input import G

#Algorithm 1: Biconnect


biconnect_augment_G, added_edges_bicon = biconnect(G.copy())

list(nx.articulation_points(biconnect_augment_G))

#[('5', '7'), ('8', '1'), ('8', '3')]
added_edges_bicon

#bcn_edges = biconnectV2(G.copy())
#bcn_edges

#print(added_edges_bicon)

#biconnect_augment_G = G.copy()
#biconnect_augment_G.add_edges_from(bcn_edges)

pos = {"1":[-2,0], "2":[-1,0.5], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1,0], "10": [1.5,-1], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(biconnect_augment_G, pos, with_labels=True)

is_planar, embedding = nx.check_planarity(biconnect_augment_G, counterexample=False)
#print(is_planar)