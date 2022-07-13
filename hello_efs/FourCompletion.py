#Algorithm 3 : Four completion
import networkx as nx
from functions import *



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
                if vertex in temp: 
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

  #print("Number of corner implying paths: ", len(cip))
  #print("Corner implying paths: ", cip)

  if len(cip) > 4:
    #print("Error! More than 4 corner implying paths")
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

