# Visualize rectangles
#import networkx as nx
#import numpy as np
#import cv2
#import matplotlib.pyplot as plt
#from shapely.geometry import Polygon
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

