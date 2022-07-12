# Use REL, T1, T2
import networkx as nx
from REL_formation import *

## Functions

def get_t_neighbors(G, T, centre, t=0):
  ordered_neighbours = order_neighbours(G, centre, clockwise=True)
  #print("FOUND ORDERED NEIGH", ordered_neighbours )

  ordered_neighbours_t = []
  if t==1 and centre=="n":
    #ordered_neighbours[::-1].append("s")
    ordered_neighbours_t = [v for v in ordered_neighbours if T.has_edge(v, centre) ]
    ans = ordered_neighbours_t + ["s"] if ordered_neighbours_t[-1] == 'w' else ordered_neighbours_t[::-1] + ["s"]
    return ans

  if t==1 and centre=="s":
    ordered_neighbours_t = [v for v in ordered_neighbours if T.has_edge(centre, v) ]
    ans = ["n"] + ordered_neighbours_t if ordered_neighbours_t[0] == 'w' else ["n"] + ordered_neighbours_t[::-1]
    return ans 
  
  if t==2 and centre=="w":
    ordered_neighbours_t = [v for v in ordered_neighbours if T.has_edge(centre, v) ]
    ans = ordered_neighbours_t + ["e"] if ordered_neighbours_t[-1] == 's' else ordered_neighbours_t[::-1] + ["e"]
    return ans
    #return ordered_neighbours_t + ["e"]
  
  if t==2 and centre=="e":
    ordered_neighbours_t = [v for v in ordered_neighbours if T.has_edge(v, centre) ]
    ans = ["w"] + ordered_neighbours_t if ordered_neighbours_t[0] == 's' else ["w"] + ordered_neighbours_t[::-1]
    return ans 

  for n in ordered_neighbours:
    if T.has_edge(centre,n) or T.has_edge(n, centre):
      ordered_neighbours_t.append(n)
  
  
  
  
  return ordered_neighbours_t 


#Create REL dictionary

## Set dict_rel

def update_cw_ccw(dict_rel):
  for T in dict_rel:
    #T_G = T1_T2[0]
    #if T == "T1": T_G = T1_T2[0]
    #if T == "T2": T_G = T1_T2[1]
    for node in dict_rel[T]:
      if 'neighbors_cw' in dict_rel[T][node]:
        neighs = dict_rel[T][node]['neighbors_cw']
        t = len(neighs)
        for i, w in enumerate(neighs):
          #if T_G.has_edge(node,w):
          dict_rel[T][node][w] = {}
          dict_rel[T][node][w]['cw'] = neighs[(i+1)%t]
          dict_rel[T][node][w]['ccw'] = neighs[(i-1)%t]


#dict_rel

def next_face_half_edge(G, v, w):
  ##print("cur(w):", w, "prev(v):",v)
  new_node = G[w][v]["ccw"]
  return w, new_node

def traverse_face(G, v, w, mark_half_edges=None):
  if mark_half_edges is None:
      mark_half_edges = set()

  face_nodes = [v]
  mark_half_edges.add((v, w))
  prev_node = v
  cur_node = w
  # Last half-edge is (incoming_node, v)
  ##print(v,w)
  incoming_node = G[v][w]["cw"] 
  

  while cur_node != v or prev_node != incoming_node:
    face_nodes.append(cur_node)
    prev_node, cur_node = next_face_half_edge(G, prev_node, cur_node)
    if (prev_node, cur_node) in mark_half_edges:
        raise nx.NetworkXException("Bad planar embedding. Impossible face.")
    mark_half_edges.add((prev_node, cur_node))

  return face_nodes

def contains_face(face, faces_list):
  for f in faces_list:
    if set(f) == set(face):
      return f
  return face


def set_node_face(REL_dict, T1_T2):
  for T in REL_dict:
    G = T1_T2[0] if T == "T1" else T1_T2[1]
    dir = ["left", "right"] if T == "T1" else ["top", "bot"]
    s_t = ["n", "s"] if T == "T1" else ["e", "w"]
    for node in REL_dict[T]:
      if node not in s_t:
        neighbors = REL_dict[T][node]['neighbors_cw']
        for i, neigh in enumerate(neighbors):
          h = (i - 1) % len(neighbors)
          prev = neighbors[h]
          #find first outgoing neigh, prev as to be incoming
          if G.has_edge(node, neigh) and G.has_edge(prev, node):
            #if node == "8" or node == "5": #print("first out ", T, (node, neigh), dir[0])
            REL_dict[T][node][dir[0]] = REL_dict[T][node][neigh][dir[0]]
            found = False
            # find next incoming
            while found == False:
              for j in range(len(neighbors)):
                k = (i + j) % len(neighbors)
                neigh = neighbors[k]
                if G.has_edge(neigh, node):
                  #if node == "8" or node == "5": #print("next in ", T,(neigh,node), dir[1])
                  REL_dict[T][node][dir[1]] = REL_dict[T][neigh][node][dir[1]]
                  break
              found = True
            break

def set_card_node_face(REL_dict, T1_T2):
  for T in REL_dict:
    G = T1_T2[0] if T == "T1" else T1_T2[1]



## Faces graph

def get_face_num(face, face_dict):
  #print("get_face_num")
  for f in face_dict:
    if type(f) != type(1):
      #print(f, face, len(set(f) - set(face)))
      min = f if len(f) < len(face) else face
      max = f if min == face else face
      #print(min, max)
      if len(set(max) - set(min)) == 0:
        #print(f, face, len(set(f) - set(face)))
        return face_dict[f]


def create_face_graph(T_graph, REL_dict, face_dict, T="T1"):
  G = nx.DiGraph()
  dir = ["left", "right"] if T=="T1" else ["bot", "top"]
  e = ["s", "n"] if T=="T1" else ["w", "e"]
  a = get_face_num(REL_dict[T][e[0]][e[1]][dir[1]], face_dict[T])
  b = get_face_num(REL_dict[T][e[0]][e[1]][dir[0]], face_dict[T])
  G.add_edge(a,b)
  for e in list(T_graph.edges): 
    #print(e)
    a = get_face_num(REL_dict[T][e[0]][e[1]][dir[0]], face_dict[T])
    b = get_face_num(REL_dict[T][e[0]][e[1]][dir[1]], face_dict[T])
    G.add_edge(a,b)
  return G


# Calculate coordinates

def distance_face_T1(face_num, face_graph, rightFace):
  all_paths = list(nx.all_simple_paths(face_graph, source=rightFace, target=face_num))
  all_paths = sorted(all_paths, key=len, reverse=True)
  #print(all_paths[0])
  return len(all_paths[0])

def set_width(node, face_G, face_dict, REL_dict, right_face):
  x_left = distance_face_T1(get_face_num(REL_dict["T1"][node]["left"], face_dict["T1"]), face_G, right_face)
  x_right = distance_face_T1(get_face_num(REL_dict["T1"][node]["right"], face_dict["T1"]), face_G, right_face)
  #print(x_left, node, x_right)
  REL_dict["T1"][node]['x_right'] = x_right
  REL_dict["T1"][node]['x_left'] = x_left

def set_card_node_width(REL_dict, face_G, right_face, left_face):
  D_T1 = distance_face_T1(left_face, face_G, right_face)
  #print("D_T1=",D_T1)
  # set x for exterior nodes
  REL_dict["T1"]['w']['x_right'] = 1
  REL_dict["T1"]['w']['x_left'] = 0

  REL_dict["T1"]['e']['x_right'] = D_T1
  REL_dict["T1"]['e']['x_left'] = D_T1 - 1

  REL_dict["T1"]['s']['x_right'] = D_T1 - 1
  REL_dict["T1"]['s']['x_left'] = 1

  REL_dict["T1"]['n']['x_right'] = D_T1 - 1
  REL_dict["T1"]['n']['x_left'] = 1

def distance_face_T2(face, face_graph, high_face):
  #print(low_face, face)
  all_paths = list(nx.all_simple_paths(face_graph, source=high_face, target=face))
  all_paths = sorted(all_paths, key=len, reverse=True)
  #print(all_paths[0])
  return len(all_paths[0])

def set_height(node, face_G, face_dict, REL_dict, top_face):
  y_bot = distance_face_T2(get_face_num(REL_dict["T2"][node]["bot"], face_dict["T2"]), face_G, top_face)
  y_top = distance_face_T2(get_face_num(REL_dict["T2"][node]["top"], face_dict["T2"]), face_G, top_face)
  #print(y_bot, node, y_top)
  REL_dict["T2"][node]['y_top'] = y_top
  REL_dict["T2"][node]['y_bot'] = y_bot

def set_card_node_height(REL_dict, face_G, bot_face, top_face):
  #print('set card height',bot_face, top_face)
  D_T2 = distance_face_T2(bot_face, face_G, top_face)
  #print("D_T2=",D_T2)
  # set y for exterior nodes
  REL_dict["T2"]['w']['y_bot'] = 0
  REL_dict["T2"]['w']['y_top'] =  D_T2

  REL_dict["T2"]['e']['y_bot'] = 0
  REL_dict["T2"]['e']['y_top'] = D_T2

  REL_dict["T2"]['s']['y_bot'] = 0
  REL_dict["T2"]['s']['y_top'] = 1

  REL_dict["T2"]['n']['y_bot'] = D_T2 - 1
  REL_dict["T2"]['n']['y_top'] = D_T2

