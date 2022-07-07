# Load Data
import networkx as nx

test_input_graph_data = {
    "1": {
        "min_width":5,
        "max_width":10,
        "min_area":30,
        "max_area":60
        },
    "2": {
        "min_width":7,
        "max_width":10,
        "min_area":40,
        "max_area":60
        },
    "3": {
        "min_width":3,
        "max_width":5,
        "min_area":10,
        "max_area":30
        },
    "4": {
        "min_width":5,
        "max_width":10,
        "min_area":40,
        "max_area":100
        },
    "5": {
        "min_width":6,
        "max_width":12,
        "min_area":30,
        "max_area":70
        },
    "6": {
        "min_width":4,
        "max_width":8,
        "min_area":10,
        "max_area":40
        },
    "7": {
        "min_width":2,
        "max_width":5,
        "min_area":10,
        "max_area":30
        },
    "8": {
        "min_width":4,
        "max_width":7,
        "min_area":10,
        "max_area":40
        },
    "adjs": [
              ["1","2"],
              ["1","3"],
              ["1","4"],
              ["2","3"],
              ["2","4"],
              ["3","4"],
              ["3","5"],
              ["5","6"],
              ["6","7"],
              ["6","8"],
              ["7","8"]
            ]    
}

#Define input graph

#Create graph
G = nx.Graph() #create empty grpah
G.add_nodes_from([(str(key), test_input_graph_data[key]) for key in test_input_graph_data if key != 'adjs']) #add nodes from the rooms dictionary
G.add_edges_from(test_input_graph_data['adjs']) # add edges from the adjacencies lsit

#Draw graph
pos = {"1":[-1,1], "2":[-2,0], "3":[0,0], "4":[-1,0.5], "5":[1,0], "6":[1,-1], "7":[0.5, -2], 
       "8":[1.5,-2], "9":[-1,0], "10": [1.5,-1], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(G, pos, with_labels=True)
#nx.draw(G, with_labels=True)