# Visualize rectangles
import networkx as nx
import numpy as np
import cv2
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from REL_to_coord import dict_rel
from REL_formation import REL_G, edge_type_color_dict
from triang_ST_cip import added_nodes_ST
from transform import final_added_edges
from REL_to_coord import exterior_nodes
## Data needed

aspect_ratio = 0.5 #0.5 - 2.0

input_graph_data = {
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

dict_room_color = {}
room_types = ["1", "2", "3", "4", "5", "6", "7", "8", "extra", "to_merge"]
#living	dining	kitchen	bath	bed	garage	stair	entrance	

for t in room_types:
  color = (0,0,0)
  if t == "1":
    color = (244,240,127)
  if t == "2":
    color = (252,171,30)
  if t == "3":
    color = (139,198,69)
  if t == "4":
    color = (233,61,38)
  if t == "5":
    color = (239,117,171)
  if t == "6":
    color = (139,215,247)
  if t == "7":
    color = (41,134,199)
  if t == "8":
    color = (93,187,71)
  if t == "extra":
    color = (211,212,212,)
  if t == "to_merge":
    color = (148,150,153)

  dict_room_color[t] = color

dict_room_color

## Visualize

#Create graph
G = nx.Graph() #create empty grpah
G.add_nodes_from([(key, input_graph_data[key]) for key in input_graph_data if key != 'adjs']) #add nodes from the rooms dictionary
G.add_edges_from(input_graph_data['adjs']) # add edges from the adjacencies lsit

#Draw graph
#nx.draw(G, pos, with_labels=True)
pos = {"1":[-1,1], "2":[-2,0], "3":[0,0], "4":[-1,0.5], "5":[1,0], "6":[1,-1], "7":[0.5, -2], 
       "8":[1.5,-2], "9":[-1,0], "10": [1.5,-1], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(G,pos, with_labels=True)

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[REL_G[u][v]['t']] for u,v in REL_G.edges]
nx.draw(REL_G, pos, edge_color=colors, with_labels=True)




blank_image = np.zeros((13,13,3), np.uint8)
blank_image[:,:,:] = (255,255,255) #set image to white

room_list = []

for room in list(REL_G.nodes):
  
  if room in list(G.nodes):
    color = dict_room_color[room]
  else:
    color = dict_room_color['extra']

  #if room == 'n' or room =='s' or room == 'w' or room=='e' or room=='1':

  
  if room not in exterior_nodes: #and room in list(G.nodes):
    ##print(room)
    x_left,x_right = dict_rel['T1'][room]['x_left'], dict_rel['T1'][room]['x_right']
    y_high,y_low = dict_rel['T2'][room]['y_top'], dict_rel['T2'][room]['y_bot']
    #x_left,x_right = dict_rel['T2'][room]['y_top'], dict_rel['T2'][room]['y_bot']
    #y_high,y_low = dict_rel['T1'][room]['x_left'], dict_rel['T1'][room]['x_right']

    #print(room, (x_left,x_right), (y_high,y_low), color)
    cv2.rectangle(blank_image, (x_left,y_high), (x_right,y_low), color,-1)
    w, h = x_right - x_left, y_high - y_low
    coords = [(x_left,y_low), (x_right,y_low), (x_right,y_high), (x_left,y_high)]
    ##print(coords)
    room_list.append(coords)
    #cv2.rectangle(blank_image,(1,1),(4,4),(0,0,0),2)
    ##print(room, (x_left,y_low),(x_left+w,y_low+h))
    #break







your_dict = {}

for i,sublist in enumerate(room_list):
    
    your_dict[i] = Polygon(sublist)

plt.figure()

for key,your_polygon in your_dict.items():
    
    plt.plot(*your_polygon.exterior.xy)

added_nodes_ST_clean = [edge[0] for edge in added_nodes_ST]
added_nodes_ST_clean

fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')

for key,geom in your_dict.items(): 
  ##print(key)
  #node_to_remove = [n for n in list(REL_G.nodes) if n not in list(G.nodes) and n not in added_nodes_ST_clean]
  #if str(key+1) not in node_to_remove:
  xs, ys = geom.exterior.xy
  #key = key + 1 
  key_name = key + 1
  if key > 7: key = 'extra' 
  else: key = key + 1 
  #if key not in list(dict_room_color.keys()):
    #key = 'extra'
  color = dict_room_color[str(key)] 
  c = (color - np.min(color))/np.ptp(color)
  if key == 'extra': c = [0.8,0.8,0.8]
  ##print(color, c) 
  axs.fill(xs, ys, alpha=0.5, fc=list(c), ec='black')
  ##print(xs, ys)
  axs.text(xs[0]+0.1, ys[0]+0.1, key_name ,fontsize='medium', va='bottom', fontfamily='serif')

plt.show()

pos = {"1":[-1,1], "2":[-2,0], "3":[0,0], "4":[-1,0.5], "5":[1,0], "6":[1,-1], "7":[0.5, -2], 
       "8":[1.5,-2], "9":[-1,0], "10": [1.5,-1], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(G,pos, with_labels=True)

extra_nodes = [n for n in list(REL_G.nodes) if n not in list(G.nodes) and n not in exterior_nodes]
extra_nodes

added_nodes_ST

final_added_edges