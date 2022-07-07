#REL Formation

## Functions

def initialize_good_vertices(G):
  """initializes the good vertices array by checking each node if its good or not"""
  good_vertices = []
  for node in G.nodes():
    if is_good_vertex(G, node):
      good_vertices.append(node)
  return good_vertices
      

def is_good_vertex(G, node):
  """
  checks if the node is good vertex or not
  Definitions:
  1) Light vertex: vertex whose degree <= 19
  2) Heavy vertex: vertex whose degree >= 20
  3) Degree 5 good vertex: (vertex who has degree 5) and (has 0 or 1  heavy neighbours)
  4) Degree 4 good vertex: (vertex who has degree 4) and
                            ((has 0 or 1 heavy neighbour) or (has 2 heavy neighbours which are not adjacent))
  5) Good vertex: Degree 4 good vertex or Degree 5 good vertex
  Note: We do not want any of the 4 boundary NESW vertices to be a good vertex since we never want to contract
        any edge connected to these vertices. LookUp: Assusmption 1 for detailed reason
  """
  if node not in ["n", "e", "s", "w"]:
      if G.degree[node] == 5:
          heavy_neighbour_count = 0
          neighbours = G.neighbors(node)
          for neighbour in neighbours:  # iterating over neighbours and checking if any of them is heavy vertex
              if G.degree[neighbour] >= 20:
                  heavy_neighbour_count += 1
          if heavy_neighbour_count <= 1:
              return True  # satisfies all conditions for degree 5 good vertex

      elif G.degree[node] == 4:
          heavy_neighbours = []
          neighbours = G.neighbors(node)
          for neighbour in neighbours:  # iterating over neighbours and checking if any of them is heavy vertex
              if G.degree[neighbour] >= 20:
                  heavy_neighbours.append(neighbour)
          if (len(heavy_neighbours) <= 1) or (
                  len(heavy_neighbours) == 2 and heavy_neighbours[0] not in G.neighbors(node) and heavy_neighbours[1] not in G.neighbors(node)):
              return True  # satisfies all conditions for degree 4 good ertex
  return False

def get_contractible_neighbour(G, v):
  v_nbr = list(G.neighbors(v)) #np.where(G[v] == 1)
  # checking if any of neighbors of the good vertex v is contractible
  # by lemma we will find one but it can be one of nesw so we need to ignore this v
  for u in v_nbr:
    if u in ["n", "e", "s", "w"]:
      continue
    contractible = True
    print('try u:', u, 'v:', v)
    #u_nbr, = np.where(G[u] == 1)
    y_and_z = list(nx.common_neighbors(G, u, v))
    if len(y_and_z) != 2:
      print("complex tri:", u, v, y_and_z)
      print("Input graph might contain a complex triangle")
    for x in v_nbr:
      if x in y_and_z or x == u:
        continue
      #x_nbr, = np.where(G[x] == 1)
      intersection = list(nx.common_neighbors(G, u, x))
      for node in intersection:
        if node not in y_and_z and node != v:
          print("not contractible:", node, "u:",u, "x:", x)
          contractible = False
          break
      if not contractible:
          break
    if contractible:
        return u, y_and_z
  return -1, []


def update_adjacency(OG, v, u):
  G = OG.copy()
  G.remove_edge(v, u)
  v_nbr = list(G.neighbors(v)).copy()
  for node in v_nbr:
      G.remove_edge(v, node)
      if node != u:
          G.add_edge(node, u)
  G.remove_node(v)
  return G

def update_good_vertices(G, good_vertices, nodes):
  print("update_good_vertices")
  for node in nodes:
    print("update", node)
    if is_good_vertex(G, node) and (node not in good_vertices):
        good_vertices.append(node)
    elif (not is_good_vertex(G, node)) and (node in good_vertices):
        good_vertices.remove(node)
  return good_vertices

def contract(OG, contractions, good_vertices):
  G = OG.copy()
  attempts = len(good_vertices)
  while attempts > 0:
      v = good_vertices.pop(0)
      u, y_z = get_contractible_neighbour(G, v)
      if u == -1:
        print(u, "not found", y_z)
        good_vertices.append(v)
        attempts -= 1
        continue
      contractions.append({'v': v, 'u': u, 'y_z': y_z, 'v_nbr': list(G.neighbors(v))})
      print('before remove:', list(G.nodes))
      G = update_adjacency(G, v, u)
      print('aftee remove:', list(G.nodes))
      print("before update good vertices")
      good_vertices = update_good_vertices(G, good_vertices.copy(), [u] + y_z)
      print("after update good vertices")

      return v, u, G, contractions, good_vertices
  return -1, -1, G, contractions, good_vertices


## Edge Contraction

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
nx.draw(four_G, pos, with_labels=True)

four_G.has_edge('3', '8')

good_verts = initialize_good_vertices(four_G)
print("initial good verts: ", good_verts)
print("n of edges:", len(list(four_G.edges)), "n of nodes:", len(list(four_G.nodes)))
v, u, contracted_G, list_contraction, good_verts = contract(four_G, [], good_verts)
print("Contracted the edge between " + str(u) + " and " + str(v))
print()
while v != -1:
  
  #break
  print("current good verts: ", good_verts)
  good_verts = initialize_good_vertices(contracted_G)
  v, u, contracted_G, list_contraction, good_verts = contract(contracted_G, list_contraction, good_verts)
  print("current good verts: ", good_verts)
  #print("n of edges:", len(list(contracted_G.edges)), "n of nodes:", len(list(contracted_G.nodes)))
  print("Contracted the edge between " + str(u) + " and " + str(v))
  print()
    
  #break

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
nx.draw(contracted_G, pos, with_labels=True)

##Trivial REL

edge_type_color_dict = {
    0: "black",
    -1: "green",
    1: "blue",
    2: "red"
}

def get_trivial_rel(end_contract_G):
  trivial_REL = nx.DiGraph()
  for node in end_contract_G.nodes:
    if node not in ["n", "e", "s", "w"]:
      trivial_REL.add_edge(node, "n", t=1)
      #G[node][self.north] = 2
      #G[self.north][node] = 0
      
      trivial_REL.add_edge("s",node, t=1)
      #G[self.south][node] = 2
      #G[node][self.south] = 0

      trivial_REL.add_edge(node, "e", t=2)
      #G[node][self.east] = 3
      #G[self.east][node] = 0

      trivial_REL.add_edge("w", node, t=2)
      #G[self.west][node] = 3
      #G[node][self.west] = 0
  return trivial_REL

trivial_REL_G = get_trivial_rel(contracted_G) #contracted_G
trivial_REL_G.add_edge("n", "w", t=0)
trivial_REL_G.add_edge("w", "n", t=0)
trivial_REL_G.add_edge("n", "e", t=0)
trivial_REL_G.add_edge("e", "n", t=0)
trivial_REL_G.add_edge("s", "w", t=0)
trivial_REL_G.add_edge("w", "s", t=0)
trivial_REL_G.add_edge("s", "e", t=0)
trivial_REL_G.add_edge("e", "s", t=0)

list(trivial_REL_G.edges)

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[trivial_REL_G [u][v]['t']] for u,v in trivial_REL_G .edges]
nx.draw(trivial_REL_G, pos, edge_color=colors, with_labels=True)

list_contraction

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[trivial_REL_G [u][v]['t']] for u,v in trivial_REL_G .edges]
nx.draw(trivial_REL_G, pos, edge_color=colors, with_labels=True)

## Functions for expansion

def handle_original_u_nbrs(OG, o, v, y, z, v_nbr):
  print("handle_original_u_nbrs")
  G = OG.copy()
  for alpha in v_nbr:
    if alpha != y and alpha != z and alpha != o:
      if G.has_edge(o, alpha):
          #G[v][alpha]["t"] = G[o][alpha]["t"]
          G.add_edge(v, alpha, t=G[o][alpha]["t"])
          #G[o][alpha]["t"] = 0
          G.remove_edge(o, alpha)
      if  G.has_edge(alpha, o):
          #G[alpha][v]["t"] = G[alpha][o]["t"]
          G.add_edge(alpha, v, t=G[alpha][o]["t"])
          #G[alpha][o]["t"] = 0
          G.remove_edge(alpha, o)
  return G

# CASES
def caseA(G, o, v, y, z, v_nbr):
  if get_ordered_neighbour_label(G, o, y, clockwise=True) == 1:
    if get_ordered_neighbour(G, o, y, True) in v_nbr:
      G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
      G.add_edge(y, v, t=2)
      G.add_edge(v, z, t=2)
      G.add_edge(o, v, t=1)
    else:
      G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
      G.add_edge(v, y, t=1)
      G.add_edge(v, z, t=2)
      G.add_edge(v, o, t=1)
      G.remove_edge(o, y) #G[o][y]["t"] = 0
      G.add_edge(y, o, t=2)
      #G.remove_edge(z, o) #G.has_edge(z,o) and G[z][o]["t"] = 0 # this line should be deleted
      #G.add_edge(o, z, t=1) # this line should be deleted
  else:
    if get_ordered_neighbour(G, o, y, True) in v_nbr:
      G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
      G.add_edge(v, y, t=1)
      G.add_edge(z, v, t=1)
      G.add_edge(o, v, t=2)
    else:
      G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
      G.remove_edge(o, z) #G.has_edge(o,z) and G[o][z]["t"]= 0
      G.add_edge(z, o, t=1)
      G.add_edge(v, o, t=2)
      G.add_edge(v, y, t=1)
      G.add_edge(v, z, t=2)
  return G

def caseB(G, o, v, y, z, v_nbr):
  G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
  G.add_edge(v, y, t=2)
  G.add_edge(z, v, t=2)
  G.add_edge(o, v, t=1)

  return G

def caseC(G, o, v, y, z, v_nbr):
  G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
  G.add_edge(y, v, t=1)
  G.add_edge(v, z, t=1)
  G.add_edge(o, v, t=2)

  return G

def caseD(G, o, v, y, z, v_nbr):
  if get_ordered_neighbour_label(G, o, y, clockwise=False) == 1:
      if get_ordered_neighbour(G, o, y, False) in v_nbr:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.add_edge(v, y, t=2)
          G.add_edge(z, v, t=2)
          G.add_edge(o, v, t=1)
      else:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          #G.remove_edge(o, y) #G[o][y]["t"] = 0 # this line should be deleted
          G.add_edge(o, y, t=2)
          G.add_edge(v, y, t=1)
          G.add_edge(z, v, t=2)
          G.add_edge(v, o, t=1)
  else:
      if get_ordered_neighbour(G, o, y, False) in v_nbr:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.add_edge(v, y, t=1)
          G.add_edge(z, v, t=1)
          G.add_edge(v, o, t=2)
      else:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.remove_edge(z, o) #G.has_edge(z,o) and G[z][o]["t"] = 0 # this line should be deleted
          G.add_edge(z, o, t=1)
          G.add_edge(z, v, t=2)
          G.add_edge(v, y, t=1)
          G.add_edge(o, v, t=2)
  return G

def caseE(G, o, v, y, z, v_nbr):
  if get_ordered_neighbour_label(G, o, y, clockwise=True) == 1:
      if get_ordered_neighbour(G, o, y, True) in v_nbr:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.add_edge(v, y, t=2)
          G.add_edge(z, v, t=2)
          G.add_edge(v, o, t=1)
      else:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          #G.remove_edge(z, o) #G.has_edge(z,o) and G[z][o]["t"] = 0 # this line should be deleted
          G.add_edge(z, o, t=2)
          G.add_edge(z, v, t=1)
          G.add_edge(v, y, t=2)
          G.add_edge(o, v, t=1)

  else:
      if get_ordered_neighbour(G, o, y, True) in v_nbr:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.add_edge(v, y, t=1)
          G.add_edge(z, v, t=1)
          G.add_edge(o, v, t=2)
      else:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.remove_edge(o, y) #G[o][y]["t"] = 0 # this line should be deleted
          G.add_edge(o, y, t=1) #G[o][y]["t"]= 1
          G.add_edge(v, o, t=2)
          G.add_edge(v, y, t=1)
          G.add_edge(z, v, t=1)
  return G

def caseF(G, o, v, y, z, v_nbr):
  print("begin caseF")
  if get_ordered_neighbour(G, o, y, True) in v_nbr:
    print("got_ordered_neighbour")
    G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
    G.add_edge(v, y, t=1)
    G.add_edge(z, v, t=1)
    G.add_edge(o, v, t=2)
  else:
    print("else")
    G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
    G.add_edge(v, y, t=1)
    G.add_edge(z, v, t=1)
    G.add_edge(v, o, t=2)
  
  return G

def caseG(G, o, v, y, z, v_nbr):
  if get_ordered_neighbour(G, o, y, True) in v_nbr:
      G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
      G.add_edge(v, y, t=2)
      G.add_edge(z, v, t=2)
      G.add_edge(v, o, t=1)
  else:
      G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
      G.add_edge(v, y, t=2)
      G.add_edge(z, v, t=2)
      G.add_edge(o, v, t=1)
  return G

def caseH(G, o, v, y, z, v_nbr):
  if get_ordered_neighbour_label(G, o, y, clockwise=True) == 1:
      if get_ordered_neighbour(G, o, y, True) in v_nbr:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.add_edge(v, y, t=2)
          G.add_edge(z, v, t=2)
          G.add_edge(v, o, t=1)
      else:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.remove_edge(y, o) #G[y][o]["t"] = 0
          G.add_edge(o, y, t=2)
          G.add_edge(y, v, t=1)
          G.add_edge(z, v, t=2)
          G.add_edge(o, v, t=1)
  else:
      if get_ordered_neighbour(G, o, y, True) in v_nbr:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.add_edge(y, v, t=1)
          G.add_edge(v, z, t=1)
          G.add_edge(v, o, t=2)
      else:
          G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
          G.remove_edge(z, o) #G.has_edge(z,o) and G[z][o]["t"] = 0
          G.add_edge(o, z, t=1)
          G.add_edge(y, v, t=1)
          G.add_edge(z, v, t=2)
          G.add_edge(o, v, t=2) 
  return G

def caseI(G, o, v, y, z, v_nbr):
  G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
  G.add_edge(y, v, t=2)
  G.add_edge(v, z, t=2)
  G.add_edge(v, o, t=1)

  return G

def caseJ(G, o, v, y, z, v_nbr):
  G = handle_original_u_nbrs(G, o, v, y, z, v_nbr)
  G.add_edge(v, y, t=1)
  G.add_edge(z, v, t=1)
  G.add_edge(v, o, t=2)

  return G


def order_neighbours(G, centre, clockwise=False):
  print("ORDER NEIGH")
  vertex_set = list(set(nx.all_neighbors(G, centre))) #list(G.neighbors(centre))
  ordered_set = [vertex_set.pop(0)]
  print("centre:",centre, "sets:",vertex_set, ordered_set)
  while len(vertex_set) != 0:
    for i in vertex_set:
      # if G has edge and edge type(t) is not 0
      #if G[ordered_set[len(ordered_set) - 1]][i]["t"] != 0 \
              #or G[i][ordered_set[len(ordered_set) - 1]]["t"] != 0:
      if G.has_edge(ordered_set[-1], i) or G.has_edge(i, ordered_set[-1]):
          ordered_set.append(i)
          vertex_set.remove(i)
          break
      elif G.has_edge(ordered_set[0], i)  or G.has_edge(i, ordered_set[0]):
          ordered_set.insert(0, i)
          vertex_set.remove(i)
          break
  print("ORDERED SET = ", ordered_set)
  current = 0
  # case: centre is the South vertex
  if centre == "s":
      if G.has_edge("w",ordered_set[0]):
          ordered_set.reverse()
  
  # case: centre is the West vertex
  elif centre == "w":
      if G.has_edge(ordered_set[0], "n"):
          ordered_set.reverse()

  # case: first vertex is in t1_leaving
  elif G.has_edge(centre,ordered_set[0]) and G[centre][ordered_set[0]]["t"] == 1:
      while G.has_edge(centre,ordered_set[current]) and G[centre][ordered_set[current]]["t"] == 1 and current < len(ordered_set)-1:
          current += 1
      if G.has_edge(centre,ordered_set[current]) and G[centre][ordered_set[current]]["t"] == 2:
          ordered_set.reverse()

  # case: first vertex is in t2_entering
  elif G.has_edge(ordered_set[0], centre) and G[ordered_set[0]][centre]["t"] == 2:
      while G.has_edge(ordered_set[current], centre) and G[ordered_set[current]][centre]["t"] == 2 and current < len(ordered_set)-1:
          current += 1
      if G.has_edge(centre,ordered_set[current]) and G[centre][ordered_set[current]]["t"] == 1:
          ordered_set.reverse()

  # case: first vertex is in t1_entering
  elif G.has_edge(ordered_set[0], centre) and G[ordered_set[0]][centre]["t"] == 1:
      while G.has_edge(ordered_set[current], centre) and G[ordered_set[current]][centre]["t"] == 1 and current < len(ordered_set)-1:
          current += 1
      if G.has_edge(ordered_set[current], centre) and G[ordered_set[current]][centre]["t"] == 2:
          ordered_set.reverse()

  # case: first vertex is in t2_leaving
  elif G.has_edge(centre,ordered_set[0]) and G[centre][ordered_set[0]]["t"] == 2:
      while G.has_edge(centre,ordered_set[current]) and G[centre][ordered_set[current]]["t"] == 2 and current < len(ordered_set)-1:
          current += 1
      if G.has_edge(ordered_set[current], centre) and G[ordered_set[current]][centre]["t"] == 1:
          ordered_set.reverse()

  if clockwise:
      ordered_set.reverse()
  print("DONE ORDERED NEIGHBORS")
  return ordered_set

def get_ordered_neighbour(G, centre, y, clockwise=False):
  print("get_ordered_neighbour")
  ordered_neighbours = order_neighbours(G, centre, clockwise)
  return ordered_neighbours[(ordered_neighbours.index(y) + 1) % len(ordered_neighbours)]

def get_ordered_neighbour_label(G, centre, y, clockwise=False):
  next = get_ordered_neighbour(G, centre, y, clockwise)
  if G.has_edge(centre, next):
    return G[centre][next]["t"] 
  else:
    return G[next][centre]["t"] 
  #if G[centre][next]["t"] == 1 or G[next][centre]["t"] == 1:
      #return 1 #T1
  #else:
      #return 2 #T2

def get_case(G, contraction):
  o = contraction['u']
  y_and_z = contraction['y_z']
  y = y_and_z[0]
  z = y_and_z[1]
  #print("if1",  G[o][y]["t"])
  if G.has_edge(o,y) and G[o][y]["t"] == 1:
      if G.has_edge(o,z) and G[o][z]["t"]== 2:
          print("o->y : T1, o->z : T2, caseA")
          return "caseA"
      elif G.has_edge(o,z) and G[o][z]["t"]== 1:
          if get_ordered_neighbour_label(G, o, y, clockwise=False) == 3:
            y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("o->y : T1, o->z : T1, caseB")
          return "caseB"
      elif G.has_edge(z,o) and G[z][o]["t"] == 2:
          print("o->y : T1, z->o : T2, caseD")
          return "caseD"
      elif G.has_edge(z,o) and G[z][o]["t"] == 1:
          print("o->y : T1, z->o : T1, caseF")
          return "caseF"
      else:
          print("ERROR o y T1")
  # change 2 ->  1, 3 -> 2
  if G.has_edge(y,o) and G[y][o]["t"] == 1:
      if G.has_edge(o,z) and G[o][z]["t"]== 2:
          y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T1, o->z : T2, caseE")
          return "caseE"
      elif G.has_edge(o,z) and G[o][z]["t"]== 1:
          y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T1, o->z : T1, caseF")
          return "caseF"
      elif G.has_edge(z,o) and G[z][o]["t"] == 2:
          print("y->o : T1, z->0 : T2, caseH")
          return "caseH"
      elif G.has_edge(z,o) and G[z][o]["t"] == 1:
          if get_ordered_neighbour_label(G, o, y, clockwise=False) == 3:
            y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T1, z->o : T1, caseI")
          return "caseI"
      else:
          print("ERROR y o T1")
          
  if G.has_edge(o,y) and G[o][y]["t"] == 2:
      if G.has_edge(o,z) and G[o][z]["t"]== 2:
          if get_ordered_neighbour_label(G, o, y, clockwise=False) == 2:
            y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("o->y : T2, o->z : T2, caseC")
          return "caseC"
      elif G.has_edge(o,z) and G[o][z]["t"]== 1:
          y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("o->y : T2,  o->z : T1, caseA swapped")
          return "caseA"
      elif G.has_edge(z,o) and G[z][o]["t"] == 2:
          print("o->y : T2, z->o : T2, caseG")
          return "caseG"
      elif G.has_edge(z,o) and G[z][o]["t"] == 1:
          print("o->y : T2, z->o : T1, caseE")
          return "caseE"
      else:
          print("ERROR o y T2")

  if G.has_edge(y,o) and G[y][o]["t"] == 2:
      if G.has_edge(o,z) and G[o][z]["t"]== 2:
          y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T2, o->z : T2, caseG")
          return "caseG"
      elif G.has_edge(o,z) and G[o][z]["t"]== 1:
          y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T2,  o->z : T1, caseD")
          return "caseD"
      elif G.has_edge(z,o) and G[z][o]["t"] == 2:
          if get_ordered_neighbour_label(G, o, y, clockwise=False) == 2:
            y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T2,  z->o : T2, caseJ")
          return "caseJ"
      elif G.has_edge(z,o) and G[z][o]["t"] == 1:
          y_and_z[0], y_and_z[1] = y_and_z[1], y_and_z[0]
          print("y->o : T2,  z->o : T1, caseH")
          return "caseH"
      else:
          print("ERROR y o T2")

def expand(G, contractions):
  function_mappings = {
    'caseA': caseA,
    'caseB': caseB,
    'caseC': caseC,
    'caseD': caseD,
    'caseE': caseE,
    'caseF': caseF,
    'caseG': caseG,
    'caseH': caseH,
    'caseI': caseI,
    'caseJ': caseJ
  }

  contraction = contractions.pop()
  print("current contraction is: ", contraction)
  case = get_case(G, contraction)
  o = contraction['u']
  v = contraction['v']
  print("before case apply  case:", case)
  #print(type(case))
  new_G = function_mappings[case](G, o, v, contraction['y_z'][0], contraction['y_z'][1], contraction['v_nbr'])
  print("after case apply")
  return new_G
  #self.node_position[o][0] = 2 * self.node_position[o][0] - self.node_position[v][0]
  #self.node_position[o][1] = 2 * self.node_position[o][1] - self.node_position[v][1]

## Edge expansion

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[trivial_REL_G [u][v]['t']] for u,v in trivial_REL_G .edges]
nx.draw(trivial_REL_G, pos, edge_color=colors, with_labels=True)

#{'v': '3', 'u': '14', 'y_z': ['n', 's'], 'v_nbr': ['14', 'e', 's', 'n']}

list_contraction

REL_G = trivial_REL_G.copy()
contractions_list = list_contraction.copy()
print("LEN:", len(contractions_list))
round = 0
while len(contractions_list) != 0:
  print()
  print("nodes:", list(REL_G.nodes))
  REL_G = expand(REL_G, contractions_list)
  round += 1
  print(round)
  if round == 3: 
    print(contractions_list[-1])
    #break


pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [-1,-0.9],
       "13": [1.5,-1], "14": [-0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [0.2,-3],"w": [-4,0]}
colors = [edge_type_color_dict[REL_G[u][v]['t']] for u,v in REL_G.edges]
nx.draw(REL_G, pos, edge_color=colors, with_labels=True)

set(list(REL_G.nodes)) == set(list(four_G.nodes))

