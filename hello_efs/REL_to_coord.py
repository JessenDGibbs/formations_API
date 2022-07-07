# Use REL, T1, T2
import networkx as nx
from REL_formation import *

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[REL_G[u][v]['t']] for u,v in REL_G.edges]
#nx.draw(REL_G, pos, edge_color=colors, with_labels=True)

is_planar, _ = nx.check_planarity(REL_G, counterexample=False)
#print(is_planar)

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

## Create T1, T2

red = [e for e in list(REL_G.edges) if REL_G[e[0]][e[1]]["t"] == 2]
blue = [e for e in list(REL_G.edges) if REL_G[e[0]][e[1]]["t"] == 1]

T1 = REL_G.copy()
T1.remove_edges_from(red)
T1.remove_edge("w", "s")
T1.remove_edge("n", "w")
T1.remove_edge("e", "s")
T1.remove_edge("n", "e")
#T1.add_edge("s", "n", t=0)
#T1.add_edge("n", "s", t=0)

posT1 = {"1":[-0.8,0.7], "2":[1.4,0.4], "3":[2.4,0], "4":[1,1], "5":[1.4,-0.5], "6":[-1,-1], "7":[0, -2], 
       "8":[-1.9,-1], "9":[0,0.9], "10": [-0.7,-1.7], "11": [0.6,-1.2], "12": [-2.9,0],
       "13": [0.5,0], "14": [0.1,-0.7], "n": [0.2,2],"e": [3,0],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[T1[u][v]['t']] for u,v in T1.edges]
#nx.draw(T1, posT1, edge_color=colors, with_labels=True)

get_t_neighbors(REL_G, T1, '3', t=1)

get_t_neighbors(REL_G, T1, 'n', t=1)

get_t_neighbors(REL_G, T1, 's', t=1)

get_t_neighbors(REL_G, T1, 'e', t=2)

get_t_neighbors(REL_G, T1, 's', t=1)



T2 = REL_G.copy()
T2.remove_edges_from(blue)
T2.remove_edge("s", "w")
T2.remove_edge("n", "w")
T2.remove_edge("e", "s")
T2.remove_edge("e", "n")
#T1.add_edge("w", "e", t=0)
#T1.add_edge("e", "w", t=0)

posT2 = {"1":[-0.8,0.7], "2":[1.4,0.4], "3":[2.4,0], "4":[1,1], "5":[1.4,-0.5], "6":[-0.5,-1.3], "7":[0, -2], 
       "8":[-1.9,-1], "9":[0,0.9], "10": [-0.7,-1.7], "11": [0.6,-1.2], "12": [-2.9,0],
       "13": [0.5,-0.2], "14": [0.1,-0.7], "n": [0.2,2],"e": [3,0],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[T2[u][v]['t']] for u,v in T2.edges]
#nx.draw(T2, posT2, edge_color=colors, with_labels=True)

get_t_neighbors(REL_G, T2, 'n', t=2)

get_t_neighbors(REL_G, T2, 'e', t=2)

get_t_neighbors(REL_G, T2, 'w', t=2)

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

dict_rel = {"T1":{n:{} for n in list(T1.nodes)}, "T2":{n:{} for n in list(T2.nodes)}}

for n in list(REL_G.nodes):
  dict_rel["T1"][n]['neighbors_cw'] = get_t_neighbors(REL_G, T1, n, t=1)
  dict_rel["T2"][n]['neighbors_cw'] = get_t_neighbors(REL_G, T2, n, t=2)

update_cw_ccw(dict_rel)

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

T1_faces = []
f = traverse_face(dict_rel["T1"], 's', 'n')
dict_rel["T1"]['s']['w']["left"] = f
dict_rel["T1"]['w']['n']["left"] = f
T1_faces.append(list(set(f)))
for e in list(T1.edges):
  ##print(e)
  f = traverse_face(dict_rel["T1"], e[0], e[1])
  #print(e, "face", f)
  ##print(e, f)
  final_face = contains_face(f,T1_faces)
  ##print(f, final_face)
  for j in range(len(final_face)):
    k = (j+1) % len(final_face)
    h = (j-1) % len(final_face)
    e_right = [final_face[j], final_face[k]]
    e_left = [final_face[j], final_face[h]]
    #if T1.has_edge()
    #print(e_right)
    dict_rel["T1"][e_right[0]][e_right[1]]["right"] = final_face
    dict_rel["T1"][e_left[0]][e_left[1]]["left"] = final_face

  if final_face == f:
    T1_faces.append(final_face)

edge = ('s', 'n')
dict_rel["T1"][edge[0]][edge[1]]["right"] = dict_rel["T1"]['s']['w']["left"]
dict_rel["T1"][edge[0]][edge[1]]["left"] = dict_rel["T1"]['s']['e']["right"]

posT1 = {"1":[-0.8,0.7], "2":[1.4,0.4], "3":[2.4,0], "4":[1,1], "5":[1.4,-0.5], "6":[-1,-1], "7":[0, -2], 
       "8":[-1.9,-1], "9":[0,0.9], "10": [-0.7,-1.7], "11": [0.6,-1.2], "12": [-2.9,0],
       "13": [0.5,0], "14": [0.1,-0.7], "n": [0.2,2],"e": [3,0],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[T1[u][v]['t']] for u,v in T1.edges]
#nx.draw(T1, posT1, edge_color=colors, with_labels=True)

T1_faces

dict_rel["T1"]["5"]

sorted(T1_faces)

len(T1_faces)

#print(len(T1_faces))
# + 1 to ad sn or we edge
#print(len(list(T1.edges)) + 1 - len(list(T1.nodes)) + 2)

T2_faces = []
f = traverse_face(dict_rel["T2"], 'w', 'e')
dict_rel["T2"]['w']['n']["top"] = f
dict_rel["T2"]['n']['e']["top"] = f
T2_faces.append(list(set(f)))
for e in list(T2.edges):
  f = traverse_face(dict_rel["T2"], e[0], e[1])
  #print(e, f)
  final_face = contains_face(f,T2_faces)
  for j in range(len(final_face)):
    k = (j+1) % len(final_face)
    h = (j-1) % len(final_face)
    e_right = [final_face[j], final_face[k]]
    e_left = [final_face[j], final_face[h]]
    dict_rel["T2"][e_right[0]][e_right[1]]["bot"] = final_face
    dict_rel["T2"][e_left[0]][e_left[1]]["top"] = final_face
  
  if final_face == f:
    T2_faces.append(final_face)

edge = ('w', 'e')
dict_rel["T2"][edge[0]][edge[1]]["top"] = dict_rel["T2"]['w']['s']["bot"]
dict_rel["T2"][edge[0]][edge[1]]["bot"] = dict_rel["T2"]['w']['n']["top"]

colors = [edge_type_color_dict[T2[u][v]['t']] for u,v in T2.edges]
#nx.draw(T2, posT2, edge_color=colors, with_labels=True)

get_t_neighbors(REL_G, T2, 'e', t=2)

traverse_face(dict_rel["T2"], 's', 'e')

#print(len(T2_faces))
# + 1 to ad sn or we edge
#print(len(list(T2.edges)) + 1 - len(list(T2.nodes)) + 2)








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
            REL_dict[T][node][dir[0]] = dict_rel[T][node][neigh][dir[0]]
            found = False
            # find next incoming
            while found == False:
              for j in range(len(neighbors)):
                k = (i + j) % len(neighbors)
                neigh = neighbors[k]
                if G.has_edge(neigh, node):
                  #if node == "8" or node == "5": #print("next in ", T,(neigh,node), dir[1])
                  REL_dict[T][node][dir[1]] = dict_rel[T][neigh][node][dir[1]]
                  break
              found = True
            break

def set_card_node_face(REL_dict, T1_T2):
  for T in REL_dict:
    G = T1_T2[0] if T == "T1" else T1_T2[1]

set_node_face(dict_rel, [T1,T2])

colors = [edge_type_color_dict[T1[u][v]['t']] for u,v in T1.edges]
#nx.draw(T1, posT1, edge_color=colors, with_labels=True)

#print(dict_rel["T1"]["8"]["left"],dict_rel["T1"]["8"]["right"])

#print(dict_rel["T1"]["w"]["left"],dict_rel["T1"]["w"]["right"])
#print(dict_rel["T1"]["e"]["left"],dict_rel["T1"]["e"]["right"])

colors = [edge_type_color_dict[T2[u][v]['t']] for u,v in T2.edges]
#nx.draw(T2, posT2, edge_color=colors, with_labels=True)

#print(dict_rel["T2"]["8"]["top"],dict_rel["T2"]["8"]["bot"])

#print(dict_rel["T2"]["s"]["top"],dict_rel["T2"]["s"]["bot"])
#print(dict_rel["T2"]["n"]["top"],dict_rel["T2"]["n"]["bot"])

#Set faces graph

## Face dict

sorted(T2_faces, key=len)

faces = {"T1":{}, "T2":{}}

i = 1
while i < len(T1_faces) - 1:
  for face in sorted(T1_faces, key=len):
    ##print(i)
    if len(face) == 3 and 'w' in face:
      faces["T1"][tuple(face)] = 0
      faces["T1"][0] = tuple(face)
    elif len(face) == 3 and 'e' in face:
      faces["T1"][tuple(face)] = len(T1_faces) - 1
      faces["T1"][len(T1_faces) - 1] = tuple(face)
    else:
      #inter = set(list(faces["T1"].keys())[list(faces["T1"].values()).index(i-1)]).intersection(set(face))
      #if len(inter) >= 2 and tuple(face) not in faces["T1"]:
        ##print(face, faces["T1"][i-1])
      faces["T1"][tuple(face)] = i
      faces["T1"][i] = tuple(face)
      i += 1
        #break

i = 1
while i < len(T2_faces) - 1:
  if i == 6: break
  for face in sorted(T2_faces, key=len):
    ##print(i)
    if len(face) == 3 and 's' in face:
      faces["T2"][tuple(face)] = 0
      faces["T2"][0] = tuple(face)
    elif len(face) == 3 and 'n' in face:
      faces["T2"][tuple(face)] = len(T2_faces) - 1
      faces["T2"][len(T2_faces) - 1] = tuple(face)
    else:
      #inter = set(list(faces["T2"].keys())[list(faces["T2"].values()).index(i-1)]).intersection(set(face))
      #if len(inter) >= 2: #print(face, faces["T2"][i-1])
      #if len(inter) >= 2 and tuple(face) not in faces["T2"]:
        ##print(face, faces["T2"][i-1])
      faces["T2"][tuple(face)] = i
      faces["T2"][i] = tuple(face)
      i += 1

colors = [edge_type_color_dict[T2[u][v]['t']] for u,v in T2.edges]
#nx.draw(T2, posT2, edge_color=colors, with_labels=True)

faces

## Faces graph

def get_face_num(face, face_dict):
  for f in face_dict:
    if type(f) != type(1):
      ##print(f, face, len(set(f) - set(face)))
      min = f if len(f) < len(face) else face
      max = f if min == face else face
      if len(set(max) - set(min)) == 0:
        ##print(f, face, len(set(f) - set(face)))
        return face_dict[f]

def create_face_graph(T_graph, REL_dict, face_dict, T="T1"):
  G = nx.DiGraph()
  dir = ["left", "right"] if T=="T1" else ["bot", "top"]
  e = ["s", "n"] if T=="T1" else ["w", "e"]
  a = get_face_num(REL_dict[T][e[0]][e[1]][dir[1]], face_dict[T])
  b = get_face_num(REL_dict[T][e[0]][e[1]][dir[0]], face_dict[T])
  G.add_edge(a,b)
  for e in list(T_graph.edges): 
    ##print(e)
    a = get_face_num(REL_dict[T][e[0]][e[1]][dir[0]], face_dict[T])
    b = get_face_num(REL_dict[T][e[0]][e[1]][dir[1]], face_dict[T])
    G.add_edge(a,b)
  return G

G1 = create_face_graph(T1, dict_rel, faces,T="T1")

posG1 = {0:[0, -3], 1:[0,-1.5], 2:[-0.8,-0.1], 3:[0,-0.6], 4:[0, 0.2], 5:[-1, 1.5], 6:[1, 1.5],7: [0.5, 0],8: [1,0.5],9: [2.5, 0.5], 10:[1,2.5], 11:[-2.2,2.5]}
#nx.draw(G1, nx.planar_layout(G1),  with_labels=True)

G2 = create_face_graph(T2, dict_rel, faces,T="T2")

#nx.draw(G2, nx.planar_layout(G2),  with_labels=True)

# Calculate coordinates

def distance_face_T1(face_num, face_graph, rightFace):
  all_paths = list(nx.all_simple_paths(face_graph, source=rightFace, target=face_num))
  all_paths = sorted(all_paths, key=len, reverse=True)
  ##print(all_paths[0])
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

def distance_face_T2(face, face_graph, low_face):
  ##print(low_face, face)
  all_paths = list(nx.all_simple_paths(face_graph, source=low_face, target=face))
  all_paths = sorted(all_paths, key=len, reverse=True)
  #print(all_paths[0])
  return len(all_paths[0])

def set_height(node, face_G, face_dict, REL_dict, bot_face):
  y_bot = distance_face_T2(get_face_num(REL_dict["T2"][node]["bot"], face_dict["T2"]), face_G, bot_face)
  y_top = distance_face_T2(get_face_num(REL_dict["T2"][node]["top"], face_dict["T2"]), face_G, bot_face)
  #print(y_bot, node, y_top)
  REL_dict["T2"][node]['y_top'] = y_top
  REL_dict["T2"][node]['y_bot'] = y_bot

def set_card_node_height(REL_dict, face_G, bot_face, top_face):
  ##print('set card height',bot_face, top_face)
  D_T2 = distance_face_T2(top_face, face_G, bot_face)
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

rightFace = get_face_num(dict_rel["T1"]['s']['n']["right"], faces["T1"])
leftFace = get_face_num(dict_rel["T1"]['s']['n']["left"], faces["T1"])

#print(rightFace, leftFace)

exterior_nodes = ["n", "e", "s", "w"]

set_card_node_width(dict_rel, G1, rightFace, leftFace)

for node in list(T1.nodes):
  if node not in exterior_nodes:
    set_width(node, G1, faces, dict_rel, rightFace)

botFace = get_face_num(dict_rel["T2"]['w']['e']["top"], faces["T2"])
topFace = get_face_num(dict_rel["T2"]['w']['e']["bot"], faces["T2"])
#print(botFace, topFace)

set_card_node_height(dict_rel, G2, botFace, topFace)

for node in list(T2.nodes):
  if node not in exterior_nodes:
    set_height(node, G2, faces, dict_rel, botFace)

dict_rel['T1']['1']