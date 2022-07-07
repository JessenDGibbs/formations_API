#Algorithm 3 : Four completion
import networkx as nx
from functions import *
from transform import PTP_G
from test_input import G

_, outer_Boundary, _, _ = find_inner_outer(PTP_G)
print("outer boundary:", outer_Boundary)
cip = find_all_CIP(PTP_G)

createPath(sorted(outer_Boundary), [])

#get_points_from_path(outer_Boundary)

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [1.5,-1], "12": [-1,-1.5],
       "13": [0.1,-1], "14": [0.7,-0.8], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(PTP_G, pos, with_labels=True)

len(PTP_G.nodes)
len(list(PTP_G.edges))

#list(PTP_G.edges)

outerBoundary = get_points_from_path(createPath(sorted(outer_Boundary), []))
print("outer boundary:", outerBoundary)
#outerBoundary = [outerBoundary[0]]+ outerBoundary[::-1][:-1] #clockwise order
#print("outer boundary:", outerBoundary)

cip

def add_nesw_vertices(OG):
  G = OG.copy()
  H = G.to_directed()

  # Get all triangles
  all_cycles = list(nx.simple_cycles(H))
  all_triangles = []
  for cycle in all_cycles:
    if len(cycle) == 3:
      all_triangles.append(cycle)

  # Get edges on outer boundary
  outer_boundary = []
  for edge in H.edges:
    count = 0
    for triangle in all_triangles:
      if edge[0] in triangle and edge[1] in triangle:
        count += 1
    if count == 2:
      outer_boundary.append(edge)

  # Get Vertex-Set of outerboundary
  outer_vertices = []
  for edge in outer_boundary:
    if edge[0] not in outer_vertices:
      outer_vertices.append(edge[0])
    if edge[1] not in outer_vertices:
      outer_vertices.append(edge[1])

  # Get top,left,right and bottom boundaries of graph
  cip = []
  loop_count = 0
  # Finds all corner implying paths in the graph
  while len(outer_vertices) > 1:
    temp = [outer_vertices[0]]
    outer_vertices.pop(0)
    for vertices in temp:
      for vertex in outer_vertices:
        temp1 = temp.copy()
        temp1.pop(len(temp) - 1)
        if (temp[len(temp) - 1], vertex) in outer_boundary:
          temp.append(vertex)
          outer_vertices.remove(vertex)
          if temp1 is not None:
            for vertex1 in temp1:
              if (vertex1, vertex) in H.edges:
                temp.remove(vertex)
                outer_vertices.append(vertex)
    cip.append(temp)
    outer_vertices.insert(0, temp[len(temp) - 1])
    if len(outer_vertices) == 1 and loop_count == 0:
      outer_vertices.append(cip[0][0])
      loop_count += 1

  check = 0
  for vertex in cip[0]:
    if (cip[len(cip) - 1][0], vertex) in H.edges and vertex != cip[len(cip) - 1][1]:
      check = 1
      break

  if check != 1:
    cip[0].insert(0, cip[len(cip) - 1][0])
    cip.pop()
  else:
    for vertex in cip[len(cip) - 2]:
      if (cip[len(cip) - 1][0], vertex) in H.edges and vertex != cip[len(cip) - 1][1]:
        check = 2
        break
    if check != 2:
      cip[len(cip) - 2] = cip[len(cip) - 2] + cip[len(cip) - 1][0]
      cip.pop()

  print("Number of corner implying paths: ", len(cip))
  print("Corner implying paths: ", cip)

  if len(cip) > 4:
    print("Error! More than 4 corner implying paths")
    exit()

  def create_cip(index):
    cip.insert(index + 1, cip[index])
    cip[index] = cip[index][0:2]
    del cip[index + 1][0:1]

  if len(cip) == 3:
    index = cip.index(max(cip, key=len))
    create_cip(index)

  if len(cip) == 2:
    index = cip.index(max(cip, key=len))
    create_cip(index)
    create_cip(index + 1)

  if len(cip) == 1:
    index = cip.index(max(cip, key=len))
    create_cip(index)
    create_cip(index + 1)
    create_cip(index + 2)


  

  def news_edges(G, cip, source_vertex):
    for vertex in cip:
        #self.edge_count += 1
        #new_adjacency_matrix[source_vertex][vertex] = 1
        #new_adjacency_matrix[vertex][source_vertex] = 1
        G.add_edge(source_vertex,vertex)

  news_edges(G, cip[0], "n")
  news_edges(G, cip[1], "e")
  news_edges(G, cip[2], "s")
  news_edges(G, cip[3], "w")

  G.add_edges_from([("n","w"), ("w","s"), ("s","e"),("e","n")])

  polar_connection = [['n', cip[0]],['e', cip[1]],['s', cip[2]],['w', cip[3]]]
                      
  

  return G, polar_connection

temp_G, polar_coord = add_nesw_vertices(PTP_G)
polar_coord

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [1.5,-1], "12": [-1,-1.5],
       "13": [0.1,-1], "14": [0.7,-0.8], "n": [-3,0],"e": [ 0.2,2],"s": [ 3,-2],"w": [ -1,-3]}
nx.draw(temp_G, pos, with_labels=True)

#four_G, card_dir_outer = FourCompletion(PTP_G, outerBoundary, cip)
four_G, card_dir_outer = add_nesw_vertices(PTP_G)
#four_G.nodes #To debug
#[1,5, 8 ,2]

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [1.5,-1], "12": [-1,-1.5],
       "13": [0.1,-1], "14": [0.7,-0.8], "n": [-3,0],"e": [ 0.2,2],"s": [ 3,-2],"w": [ -1,-3]}
nx.draw(four_G, pos, with_labels=True)

is_planar, _ = nx.check_planarity(four_G, counterexample=False)
print(is_planar)

max(list(G.nodes))

def to_my_int(G, node):
  if node == "n":
    return 14
  if node == "e":
    return 15
  if node == "s":
    return 16
  if node == "w":
    return 17
  else:
    return int(node) - 1

len(list(PTP_G.nodes))

edges = [[to_my_int(four_G, e[0]), to_my_int(four_G, e[1])] for e in list(PTP_G.edges)]

len(edges)

graph_info = [18, 29, [[0, 1],[0, 2],[0, 8],[0, 11],
                      [1, 2],[1, 3],[1, 8],[2, 3],[2, 4],[2, 11],[2, 12],
                      [3, 8],[4, 5],[4, 10],[4, 12],[4, 13],
                      [5, 6],[5, 7],[5, 9],[5, 10],[5, 13],[6, 9],[6, 10],
                      [7, 9],[7, 11],[7, 12],[7, 13],
                      [11, 12],[12, 13]]]

len(graph_info[2])

edges