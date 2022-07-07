#Functions

def findsubsets(s, n):
    return list(itertools.combinations(s, n))

##Biconnect

def setBlockAttr(G):
  dict_block = {}
  for i, block in enumerate(sorted(nx.biconnected_components(G), key=len)):
    #print(i)
    for n in block:
      if n not in dict_block:
        dict_block[n] = [i]
        #print(n)
      else:
        dict_block[n].append(i)
  return dict_block

def same_Component(nxgraph,u,v):
    """
    Args: 
        nxgraph: an instance of Networkx graph object
        u,v: vertices to be checked
    
    Returns:
        boolean: TRUE if vertices are in the same biconnected component else FALSE.
    """
    components = list(nx.biconnected_components(nxgraph))
    for itr in range(len(components)):
        if (u in components[itr]) and (v in components[itr]):
            return True
    return False

def adj(G,v):
  neigh = list(G.neighbors(v))
  adj_node = []
  #comps = sorted(nx.biconnected_components(G), key=len)
  comps = list(nx.biconnected_components(G))
  print("comps:",comps)
  odd = True
  for block in comps:
    #block = sort_by_degree(G, list(block))
    block = sorted(block)
    if v in block:
      for n in block:
        if n not in adj_node and n != v:
          adj_node.append(n)
    
  print("adjs:", adj_node)
  return adj_node

def sort_by_degree(G, aList):
  new_list = [aList[0]]
  for node in aList[1:]:
    if G.degree[node] >= G.degree[new_list[-1]]:
      new_list.append(node)
    else:
      index = 0
      if len(new_list) > 1:
        index = -2
      new_list.insert(index, node)
  return new_list

from os import remove
import numpy as np
import networkx as nx


def is_Edge_Biconnected(nxgraph):
    """returns a boolean representing whether the graph
     is edge biconnected or not.
    Args:
        nxgraph: An instance of NetworkX Graph object.
    Returns:
        boolean: indicating TRUE if biconnected, FALSE otherwise.
    """
    return nx.is_k_edge_connected(nxgraph, k=2)

def is_Vertex_Biconnected(nxgraph):
    """returns a boolean representing whether the graph 
    is vertex biconnected or not.
    
    Args:
        nxgraph: An instance of NetworkX Graph object.
    
    Returns:
        boolean: indicating TRUE if biconnected, FALSE otherwise.
    """
    return nx.is_biconnected(nxgraph)

def edge_Biconnect(nxgraph):
    """ checks if a graph needs to be biconnected 
    and returns edges to be added to make it biconnected
    
    Args:
        # matrix: Adjacency matrix of the said graph.
        nxgraph(for testing): an instance of NetworkX graph object.
    
    Returns:
        ebicon_edges: Edges to be added to make the graph edge biconnected
    """
    # nxgraph = nx.from_numpy_matrix(matrix)
    bicon_edges = []
    if not is_Edge_Biconnected(nxgraph):
        ebicon_edges = sorted((nx.k_edge_augmentation(nxgraph, k=2)))
    return ebicon_edges

def get_Cutvertices(nxgraph):
    """
    Args:
        nxgraph: an instance of NetworkX graph object.
    
    Returns:
        articulation_list: List of all articulation points in the graph
    """
    articulation_list = list(nx.articulation_points(nxgraph))
    return articulation_list

def get_Biconnected_Components(nxgraph):
    """
    Args:
        nxgraph: an instance of NetworkX graph object.
    
    Returns:
        components: Set of biconnected components.
    """
    components = nx.biconnected_components(nxgraph)
    return components

def same_Component(nxgraph,u,v):
    """
    Args: 
        nxgraph: an instance of Networkx graph object
        u,v: vertices to be checked
    
    Returns:
        boolean: TRUE if vertices are in the same biconnected component else FALSE.
    """
    components = list(get_Biconnected_Components(nxgraph))
    for itr in range(len(components)):
        if (u in components[itr]) and (v in components[itr]):
            return True
    return False

def biconnectV1(nxgraph):
    """
    Args:
        # matrix: Adjacency matrix of the said graph.
        nxgraph(for testing): an instance of NetworkX graph object.
    
    Returns:
        bicon_edges: Edges to be added to make the graph biconnected
    """
    # nxgraph = nx.from_numpy_matrix(matrix)
    articulation_points = get_Cutvertices(nxgraph)
    bicon_edges = set()
    added_edges = set()
    removed_edges = set()
    for i in range(len(articulation_points)): 
        neighbors = list(nx.neighbors(nxgraph,articulation_points[i]))
        for j in range(0,len(neighbors)-1):
            if not same_Component(nxgraph,neighbors[j],neighbors[j+1]):
                added_edges.add((neighbors[j],neighbors[j+1]))
                if(articulation_points[i], neighbors[j]) in added_edges\
                    or (neighbors[j],articulation_points[i]) in added_edges:
                    removed_edges.add((articulation_points[i],neighbors[j]))
                    removed_edges.add((neighbors[j],articulation_points[i]))
                if (articulation_points[i],neighbors[j+1]) in added_edges\
                    or (neighbors[j+1],articulation_points[i]) in added_edges:
                    removed_edges.add((articulation_points[i],neighbors[j+1]))
                    removed_edges.add((neighbors[j+1],articulation_points[i]))
    bicon_edges = added_edges - removed_edges
    nxgraph.add_edges_from(bicon_edges)
    return nxgraph, bicon_edges


def adj_group_by_bloc(G,v):
  neigh = list(G.neighbors(v))
  print("neigh:", neigh)
  #comps = sorted(nx.biconnected_components(G), key=len)
  comps = list(nx.biconnected_components(G))

  print("comps:",comps)
  adj_node = [ n for block in comps for n in neigh if n in block ]
  print("new neigh:",adj_node)
  return adj_node

def biconnect(OG):
  G = OG.copy()
  added = []
  removed = []
  cut = list(nx.articulation_points(G))
  cutVertices = cut
  cutVertices = sort_by_degree(G, cut)

  for v in cutVertices:
    print(v)
    #update_block_attr(G)
    U = adj(G,v)
    #U = adj_group_by_bloc(G,v)
    #print(adj_group_by_bloc(G,v))
    #U = list(G.neighbors(v))
    #OG = G.copy()
    current_G = G.copy()
    for j in range(len(U)):
      print("articulations:",list(nx.articulation_points(G)))
      k = (j+1)%len(U)
      print("j,k,",j,k)
      e = (U[j], U[k])
      #if len(set(G.nodes[U[j]]["block"]).intersection(G.nodes[U[k]]["block"])) == 0:
      #print(U[j],U[k])
      if same_Component(current_G,U[j],U[k]): print("same:", U[j],U[k])
      if same_Component(current_G,U[j],U[k]) == False:
        #if U[j] in cutVertices or U[k] in cutVertices:
        is_planar, _ = nx.check_planarity(G, counterexample=False)
        if is_planar and len(list(nx.articulation_points(G))) == 0: break
        print("adding edge: ", (U[j], U[k]))
        G.add_edge(U[j], U[k])
        added.append((U[j], U[k]))
      if (v, U[j]) in added:
        print("before removing",(v, U[j]))
        removed.append((v, U[j]))
        if G.has_edge(v, U[j]):
          print("removing",(v, U[j])) 
          G.remove_edge(v, U[j])
          #added.remove((v, U[j]))
          #if (U[j], v) in added:added.remove((U[j], v))

      if (v, U[k]) in added:
        print("before removing",(v, U[k]))
        removed.append((v, U[j]))
        if G.has_edge(v, U[k]): 
          print("removing",(v, U[k]))
          G.remove_edge(v, U[k])
          #added.remove((v, U[k]))
          #if (U[k], v) in added:added.remove((U[k], v))
      
      #if len(list(nx.articulation_points(G))) == 0: break
  print("added:", added, "removed:", removed)
  added_nodes = set(added) - set(removed)      
  return G, list(added_nodes)

##other

def find_all_triangles(OG):
  edge_use_count = {}
  G = OG.copy()
  # Assume G is undirected
  nodeNeighbours = {
    # The filtering of the set ensure each triangle is only computed once
    # assumme only numbers
    node: set(n for n in edgeInfos.keys() if int(n) > int(node))
    for node, edgeInfos in G.adjacency()
  }
  all_triangles = []
  for node1, neighbours in nodeNeighbours.items():
    for node2 in neighbours:
      AND = (neighbours & nodeNeighbours[node2])
      #print("n1:", node1, "n2:", node2, "neigh1:",neighbours, "neigh2:", nodeNeighbours[node2], "and:", AND)
      for node3 in AND:
        all_triangles.append([node1, node2, node3])
        e1, e2, e3 = (node1, node2), (node2, node3), (node3, node1)
        for e in [e1,e2, e3]:
          if e not in edge_use_count: 
            edge_use_count[e] = 0 
            edge_use_count[e[::-1]] = 0 
          edge_use_count[e] +=1
  return all_triangles, edge_use_count

def isElementaryCycle(tri, allTriangles):
  iter =list(itertools.permutations(tri))
  #print(tri, "iter:", iter)
  for triangle in iter:
    if list(triangle) in allTriangles:
      #print("in all:", triangle)
      return True
  return False

def remove_edge_with_different_count(OG, base):
  G = OG.copy()
  _ , edge_count = find_all_triangles(G)
  #print("base:",base)
  e1, e2, e3 = (base[0], base[1]),(base[1], base[2]),(base[2], base[0])
  #count_dict_base[e1], count_dict_base[e2], count_dict_base[e3] = 0, 0, 0
  count_e1 = edge_count[e1] + edge_count[e1[::-1]]
  count_e2 = edge_count[e2] + edge_count[e2[::-1]]
  count_e3 = edge_count[e3] + edge_count[e3[::-1]]

  #print("counts:", count_e1, count_e2, count_e3)
  node_with_count = [(base[0], max(count_e3, count_e1)),(base[1], max(count_e2, count_e1)),(base[2], max(count_e2, count_e3))]
  #print(node_with_count)

  min_count = min(count_e1, count_e2, count_e3)
  new_base = []

  for node in node_with_count:
    if node[1] <= min_count:
      new_base.append(node[0])

  new_base = tuple(new_base)
  #print("new base:",new_base)
  return new_base

def valid_base(OG, base):
  G = OG.copy()
  return base == remove_edge_with_different_count(G, base)

def findST(OG):
  G = OG.copy()
  allTriangles, _  = find_all_triangles(G)
  #print('all:', allTriangles)
  # return the four face of a triangular pyramid
  four_points_subset = findsubsets(list(G.nodes), 4)
  for four in four_points_subset:
    pyramid = []
    pyramid_found = True
    for triangle in findsubsets(four, 3):
      pyramid.append(triangle)
      if isElementaryCycle(triangle, allTriangles) == False:
        pyramid_found = False
        break
    if pyramid_found == True:
      print("part of a ST:",four)
      return [four, pyramid]
  return []

def removeST(OG, pyramid):
  G = OG.copy()
  #remove base connected to other triangles outside the pyramid
  possible_bases = [b for b in pyramid[1] if valid_base(G, b) == True]
  print("possible bases:", possible_bases)
  base = random.choice(possible_bases)
  #base = [2,3, 4] to replicate
  print("base:", base)
  #print(remove_edge_with_different_count(OG, base))
  #print("valid:",valid_base(G, base))
  a, b, top = base #random.sample(base, 3)
  if G.has_edge(a,b): G.remove_edge(a,b) 
  else: G.remove_edge(b,a)
  print("removed:",(a,b))
  d = str(G.number_of_nodes() + 1)
  G.add_edge(a, d)
  print("add:",(a,d))
  G.add_edge(b, d)
  print("add:",(b,d))
  G.add_edge(top, d)
  print("add:",(top,d))
  return G

# check if graph has a ST based on p.5 paper
def has_ST(OG):
  G = OG.copy()
  clean_t, _ = find_all_triangles(G)
  print(clean_t)
  print("n elementary circuit:", len(clean_t), " vs", (G.number_of_edges() - G.number_of_nodes() + 1))
  print("n of edge:", G.number_of_edges(), " n of nodes", G.number_of_nodes(), " +1")
  check = (len(clean_t) == (G.number_of_edges() - G.number_of_nodes() + 1))
  if check == True: return False
  return True


def find_inner_outer(OG):
  G = OG.copy()
  _, edge_use_count = find_all_triangles(G)
  outer_v = []
  inner_v = []
  outer_edges = []
  inner_edges = []
  for e in edge_use_count:
    total = edge_use_count[e] + edge_use_count[e[::-1]]
    for v in e:
      if total == 1 and v not in outer_v: outer_v.append(v)
      if total == 1 and e not in outer_edges and e[::-1] not in outer_edges: outer_edges.append(e)

  for e in edge_use_count:
    total = edge_use_count[e] + edge_use_count[e[::-1]]
    for v in e:
      if total > 1 and v not in inner_v and v not in outer_v: inner_v.append(v)
      if e not in outer_edges and e[::-1] not in outer_edges: inner_edges.append(e)
  return outer_v, outer_edges, inner_v, inner_edges

def find_shortcuts(G):
  shortcuts = []
  shortcut_points = []
  outer_v, outer_edges, inner_v, inner_edges = find_inner_outer(G)
  for e in inner_edges:
    if ((e[0] in outer_v and e[1] in outer_v) and 
        (e not in outer_edges and e not in shortcuts and e[::-1] not in shortcuts)):
      shortcuts.append(e)
      if e[0] not in shortcut_points: shortcut_points.append(e[0])
      if e[1] not in shortcut_points: shortcut_points.append(e[1])

  return shortcuts, shortcut_points

def find_CIP(G, start, end, path, flip=False):
  _, outer_boundary, _, _ = find_inner_outer(G)
  _, shortcut_points = find_shortcuts(G)
  path.append(start)
  #print("start:", start, " end:", end, " path:", path, " bool:",(start==end))
  if start == end:
    return path
  else:
    for e in outer_boundary:
      #print("e=",e)
      ans = []
      old_path = path.copy()
      if start in e:
        for node in e:
          if node != start and node not in path and (node not in shortcut_points or node == end):
            #start = node
            ans = find_CIP(G, node, end, path, flip)
            #print("after ans:", ans)
            if len(ans) > 0 and ans[-1] == end:
              return ans
      if ans == []:
        path = old_path
        continue
    if flip == True:
      return []
    else:
      # no valid edge with the star, flip end and start
      return find_CIP(G, end, start, [], flip=True)

def find_all_CIP(G):
  all_cip = []
  shortcuts, _ = find_shortcuts(G)
  for e in shortcuts:
    a_cip = find_CIP(G, e[0], e[1], [])
    print("shortcut:", e, "cip:", a_cip)
    if len(a_cip) > 0:
      all_cip.append(a_cip)

  return all_cip

def remove_shortcut(OG, short_cut):
  G = OG.copy()
  a,b = short_cut
  if G.has_edge(a,b): G.remove_edge(a,b) 
  else: G.remove_edge(b,a)
  print("removed:",(a,b))
  d = str(G.number_of_nodes() + 1)
  G.add_edge(a, d)
  print("add:",(a,d))
  G.add_edge(b, d)
  print("add:",(b,d))
  return G

def transform(OG, edge):
  G = OG.copy()
  _, edge_use_count = find_all_triangles(G)
  edge = edge
  nbd_u = list(G.neighbors(edge[0]))
  nbd_v = list(G.neighbors(edge[1]))
  total = edge_use_count[edge] + edge_use_count[edge[::-1]]
  # if edge is exterior edge
  if total == 1:
    x = list(set(nbd_u).intersection(set(nbd_v)))[0]
    a = str(G.number_of_nodes() + 1)
    print("edge:", edge,"x:",x, "a:", a)
    G.add_node(a)
    G.add_edges_from([(a, x), (a, edge[0]), (a,edge[1])])
    G.remove_edge(*edge)
  else:
    x,y = list(set(nbd_u).intersection(set(nbd_v)))
    a = str(G.number_of_nodes() + 1)
    print("edge:", edge,"x,y:",x,y,  "a:", a)
    G.add_node(a)
    G.add_edges_from([(a, x), (a, y), (a, edge[0]), (a,edge[1])])
    G.remove_edge(*edge)
  
  return G

# order edge list like a path, assume initial edge list sorted and all edge conencted
def createPath(edge_list, path):
  path.append(edge_list[0])
  edge_list.pop(0)
  if len(edge_list) == 0:
    return path
  else:
    e_list = edge_list.copy()
    for i in range(len(e_list)):
      a,b = e_list[i]
      #print("end:", path[-1][1], "a:",a,"b:",b)
      if path[-1][1] == a:
        edge_list.pop(i)
        edge_list.insert(0, (a,b))
        
        return createPath(edge_list, path)
      if path[-1][1] == b:
        edge_list.pop(i)
        edge_list.insert(0, (b,a))
        
        return createPath(edge_list, path)
    return path

def get_points_from_path(path):
  points = []
  for e in path:
    points.append(e[0])
  return points

def find_all_path(OG, start, end, path, all_paths):
  #G = OG.copy()
  _, outer_boundary, _, _ = find_inner_outer(G)
  outer_boundary = createPath(sorted(outer_Boundary), [])
  path.append(start)
  #print("start:", start, " end:", end, " path:", path, " bool:",(start==end))
  if start == end:
    return path
  else:
    for e in outer_boundary:
      #print("e=",e)
      ans = []
      old_path = path.copy()
      #print("start:", start,"e:", e, " end:", end, " path:", path)
      if start in e:
        for node in e:
          if node != start and node not in path:
            #start = node
            #print("start:", start,"node:", node, " end:", end, " path:", path)
            ans = find_all_path(G, node, end, path, all_paths)
            #print("after ans:", ans)
            if len(ans) > 0 and ans[-1] == end:
              all_paths.append(ans)
              #path = path[:-1]
              #start = ans[0]
              #node = path[-1]
              
              #continue
      #if ans == []:
      path = old_path
      #print("new start:", start, " end:", end, " path:", path)
      #print()
      #continue
   
    return all_paths


def add_edges(G, v, vertices):
  for n in vertices:
    G.add_edge(v,n)

def is_overlaping_path(p1,p2):
  #check if there is the same point in both path
  # start and end not counted
  for a in p1[1:-1]:
    for b in p2[1:-1]:
      if a == b:
        return True
  return False

def circular_range(start, end, modulo):
    if start > end:
        while start < modulo:
            yield start
            start += 1
        start = 0

    while start < end:
        yield start
        start += 1

print(list(circular_range(7, 0+1, 11)))

#Four-completion Algorithm 3
def FourCompletion(OG, boundary, cips):
  while True:
    G = OG.copy()
    #if boundary is triangle
    if len(boundary) == 3:
      v1, v2, v3 = boundary
      cornerPoints = [v1, v2, v3, v1] #not sur if last point is v1 or 1
    else:
      chosen_points = []
      min_index = len(boundary)
      while min_index > len(boundary) - (4-len(cips)):
        for c in cips:
          r = random.choice(c)
          while r in chosen_points:
            r = random.choice(c)
          chosen_points.append(r)
        print("chosen from cips:",chosen_points)
        indexes = [boundary.index(x) for x in chosen_points]
        min_index = max(indexes)
      print(indexes, min_index, boundary[min_index:])
      if len(chosen_points) < 4:
        for i in range(len(chosen_points), 4):
          p = random.choice(boundary[min_index:])
          while p in chosen_points:
            p = random.choice(boundary[min_index:])

          chosen_points.append(p)
      #cornerPoints = chosen_points
      cornerPoints = [point for point in boundary if point in chosen_points] #points in the order of the boundary
      #cornerPoints = [str(p) for p in[1, 5, 8, 2]]
    print("cornerPoints:",cornerPoints)
    #p1 = sorted(find_all_path(G, cornerPoints[0], cornerPoints[1], [], []), key=len)[0] 
    p1 = [boundary[i] for i in list(circular_range(boundary.index(cornerPoints[0]), boundary.index(cornerPoints[1])+1, len(boundary)))]
    #all_p = find_all_path(G, cornerPoints[1], cornerPoints[2], [], [])
    #p2 = sorted([p for p in all_p if is_overlaping_path(p1,p) == False], key=len)[0]
    p2 = [boundary[i] for i in list(circular_range(boundary.index(cornerPoints[1]), boundary.index(cornerPoints[2])+1, len(boundary)))]
    #all_p = find_all_path(G, cornerPoints[2], cornerPoints[3], [], [])
    #p3 = sorted([p for p in all_p if is_overlaping_path(p2,p) == False], key=len)[0]
    p3 = [boundary[i] for i in list(circular_range(boundary.index(cornerPoints[2]), boundary.index(cornerPoints[3])+1, len(boundary)))]
    #all_p = find_all_path(G, cornerPoints[3], cornerPoints[0], [], []) 
    #p4 = sorted([p for p in all_p if is_overlaping_path(p3,p) == False], key=len)[0]
    p4 = [boundary[i] for i in list(circular_range(boundary.index(cornerPoints[3]), boundary.index(cornerPoints[0])+1, len(boundary)))]

    print("all path",p1,p2,p3,p4)


    G.add_nodes_from("nesw")
    add_edges(G, "n", p1)
    add_edges(G, "e", p2)
    add_edges(G, "s", p3)
    add_edges(G, "w", p4)

    polar_connection = [['n', p1],['e', p2],['s', p3],['w', p4]]

    G.add_edges_from([("n","w"), ("w","s"), ("s","e"),("e","n")])

    is_planar, _= nx.check_planarity(G)
    print("is planar:",is_planar)
    if is_planar == True: 
      break
    #break

  return G, polar_connection
