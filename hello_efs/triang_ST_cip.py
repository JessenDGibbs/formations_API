from functions import *
from triangulation import *
import networkx as nx

from biconnect import biconnect_augment_G
#Triangulation, remove ST, remove extra CIPs

## Triangulation

triang_G, added_edges_triang = triangulate_MCSM(biconnect_augment_G, randomized=False, reduce_graph=False)["H"]

#[('8', '5')]
added_edges_triang 

pos = {"1":[-2,0], "2":[-1,0.5], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1,0], "10": [1.5,-1], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(triang_G, pos, with_labels=True)

is_planar, embedding = nx.check_planarity(triang_G, counterexample=False)
print(is_planar)

##Remove ST

triang_G.has_edge("1","3")

triang_G.has_edge("3","1")

def form_cycle(G, node_list):
  for j in range(len(node_list)):
    k = (j+1) % len(node_list)
    if G.has_edge(node_list[j], node_list[k]) == False:
      #print("NO:", (node_list[j], node_list[k]))
      return False
  return True

def find_non_pyramid_ST(G):
  print("NON PYRAMID")
  faces = all_faces(G)
  faces_set = [set(f) for f in faces]
  ST = []
  done = []
  for f in faces:
    neigh = [list(G.neighbors(node)) for node in f]
    s1, s2, s3 = set.intersection(*map(set,[neigh[0], neigh[1]])), set.intersection(*map(set,[neigh[1], neigh[2]])), set.intersection(*map(set,[neigh[2], neigh[0]]))
    #print("s1,s2,s3",s1,s2,s3)
    #if len(s1) == 1 and len(s2) == 1 and len(s3) ==1:
    inter = (set.intersection(*map(set,[neigh[0], neigh[1]])) and set.intersection(*map(set,[neigh[1], neigh[2]]))) and set.intersection(*map(set,[neigh[2], neigh[0]]))
    common = set.intersection(s1,s2,s3)
    s1,s2,s3 = {p for p in s1 if p not in f and p not in common}, {p for p in s2 if p not in f and p not in common}, {p for p in s3 if p not in f and p not in common}
    #print("s1,s2,s3",s1,s2,s3)
    if len(s1) == 1 and len(s2) == 1 and len(s3) == 1:
      #set_list = [s1,s2,s3]
      #inter = [p for s in set_list for p in s if p not in f and p not in common]
      inter = [p for s in [s1,s2,s3] for p in s]
      points = set(inter + f)
      print("face:",f,"inter:", inter, "intersection:", common, set(inter) in faces_set, form_cycle(G, inter), points not in done, len(inter) == 3)
      
      if set(inter) in faces_set and points not in done and len(inter) == 3:
        done.append(points)
        #ST.append([inter, f, [[inter[0], f[0], f[1]], [inter[1], f[1], f[2]],[inter[2], f[2], f[0]]]])
        #ST.append([inter, f, [[inter[0], f[0], f[1]], [inter[1], f[1], f[2]],[inter[2], f[2], f[0]]]])
        possible = [[inter[0], [f[0], f[1]]], [inter[1], [f[1], f[2]]], [inter[2], [f[2], f[0]]]]
        min = [10, [f[0], f[1]]]
        best = []
        for poss in possible:
          triangle = [poss[0]] + poss[1]
          usage = edge_use_cycle(G, tuple(poss[1]))
          print("usage", usage, "e:", poss[1])
          cycles = [set(c) for c in usage[1] if len(set(c).intersection(set(triangle))) < 3]
          print("cycles:", cycles, "edge:",  tuple(poss[1]), "points:",points, "tri:", triangle)
          if len(cycles) <= min[0]:
            #extra = [[]]
            extra = [[p for c in cycles for p in c if p not in triangle and p not in common]]
            min = [len(cycles), poss[1], extra]
            print('min:',min)
            best = poss + extra
        ST.append(best)
        #ST.append([inter[0], [f[0], f[1]]])
        #ST.append([inter[1], [f[1], f[2]]])
        #ST.append([inter[2], [f[2], f[0]]])
  return ST


def detect_ST(OG):
  G = OG.copy()
  all_STs = []

  for node in list(G.nodes):
    node_neigh = list(G.neighbors(node))
    if form_cycle(G, node_neigh) == True : #and len(node_neigh) == 3
      #top/center node, [base]
      ST = [node, node_neigh]
      all_STs.append(ST)
  all_STs.sort(key=lambda x: len(x[1]))
  print("all_STS", all_STs)
  return  all_STs
  

def choose_random_edge_from_path(G, path, top=[]):
  if len(path) > 3:
    #['4', ['1', '2', '3', '5', '8']]
    all_node_by_deg = sorted(G.degree, key=lambda x: x[1], reverse=True)
    nodes_by_deg = [pair[0] for pair in all_node_by_deg if pair[0] in path]
    print(nodes_by_deg)
    print(path, [G.degree(n) for n in path])
    print("hi")
    path = nodes_by_deg[0:3]
    #return [(0,0), []]
  #else:
  points = path + top
  min = [10, (path[0], path[1])]
  tries = 3
  for j in range(len(path)):
    #j = random.randint(0, len(path)-1)
    k = (j+1)%len(path)
    usage = edge_use_cycle(G, (path[j], path[k]))
    print("usage", usage)
    cycles = [set(c) for c in usage[1] if len(set(c).intersection(set(points))) < 3]
    print(j,k,"try:", tries, "cycles:", cycles, "edge:",  (path[j], path[k]), points)
    #tries -= 1
    if len(cycles) <= min[0]:
      min = [len(cycles), (path[j], path[k]), [p for c in cycles for p in c if p not in points]]
      print("*****MIN*******:", min)
    #if len(cycles) ==0:
      #return min[1:]
      #return (path[j], path[k])
    

  return min[1:]

def remove_ST(OG, ST):
  G = OG.copy()

  top, a, b, extra_points = ST
  print("chosen a,b = ", a,b, "usage:", edge_use_cycle(G, (a,b)), "top:", top, "extra:",extra_points)

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

  for p in extra_points:
    print("extra add:",(p,d))
    G.add_edge(p, d)
  return G, d

def all_faces(G):
  unsorted_cycles = [c for c in list(nx.simple_cycles(G.copy().to_directed())) if len(c) == 3]
  all_elementary_cycles = []
  for c in unsorted_cycles:
    triangle = list(set(c))
    if triangle not in all_elementary_cycles:
      all_elementary_cycles.append(triangle)
  print("len check:",len(all_elementary_cycles), len(unsorted_cycles))
  return sorted(all_elementary_cycles)

def edge_use_cycle(G, e):
  cycles = all_faces(G)
  my_cycles = []
  for c in cycles:
    if e[0] in c and e[1] in c:
      my_cycles.append(c)
  return [e, my_cycles]


unsorted_cycles = [c for c in list(nx.simple_cycles(triang_G.copy().to_directed())) if len(c) == 3]
all_elementary_cycles = []
for c in unsorted_cycles:
  triangle = list(set(c))
  if triangle not in all_elementary_cycles:
    all_elementary_cycles.append(triangle)
print(len(all_elementary_cycles), len(unsorted_cycles))
sorted(all_elementary_cycles)

all_faces(triang_G)

detect_ST(triang_G)

pos = {"1":[-2,0], "2":[-1,0.5], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1,0], "10": [1.5,-1], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(triang_G, pos, with_labels=True)

list(triang_G.neighbors("2"))

added_nodes_ST = []

# we can loop the process to remove multiple ST
noST_G = triang_G.copy()
c = 0
while has_ST(noST_G) == True:
  #sphinx = findST(noST_G)
  sphinx = detect_ST(noST_G)
  print("NON PY")
  print("PYR:",find_non_pyramid_ST(noST_G))
  if len(sphinx) == 0:
    sphinx = find_non_pyramid_ST(noST_G)[0]
    top, edge, extra_points = sphinx
  else:
    sphinx = sphinx[0]
    top, base = sphinx
    edge, extra_points = choose_random_edge_from_path(noST_G, base, top=[top])
  print("****pyramid:",sphinx)
  #noST_G = removeST(noST_G, sphinx)
  
  #break
  #top, base = sphinx
  #edge, extra_points = choose_random_edge_from_path(noST_G, base, top=[top])
  pointA, pointB = edge
  sep_triangle = [top, pointA, pointB, extra_points]
  noST_G, added_node = remove_ST(noST_G, sep_triangle)
  added_nodes_ST.append([added_node, edge])
  print("**DONE** \n")
  print("hasST? ", has_ST(noST_G))
  print(detect_ST(noST_G))
  print(find_non_pyramid_ST(noST_G))
  print()
  #if c == 1: break
  print("*************C***********", c)
  c +=1
# (2,3) or (3,2) give the same result as the paper

#['3', ['1', '2', '4', '5', '8']]
#'8', '4', '5'

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(noST_G, pos, with_labels=True)

is_planar, embedding = nx.check_planarity(noST_G, counterexample=False)
print(is_planar)

##Remove CIPs

_, outer_Boundary, _, _ = find_inner_outer(noST_G)
cip = find_all_CIP(noST_G)

new_G = noST_G.copy()
while len(cip) > 4:
  # remove a shortcut
  shortcut = random.choice(find_shortcuts(noST_G)[0])
  print(shortcut)
  new_G = remove_shortcut(noST_G.copy(), shortcut)
  cip = find_all_CIP(new_G)
  

pos = {"1":[-2,0], "2":[-1,0.4], "3":[0,0], "4":[-1,1], "5":[1,0], "6":[1,-1], "7":[1.5, -2], 
       "8":[0.5,-2], "9":[-1.5,0.6], "10": [1,-2], "11": [0.5,-0.5], "12": [0.2,0.5],
       "13": [0.1,-1], "n": [0.2,2],"e": [3,-2],"s": [-1,-3],"w": [-3,0]}
nx.draw(new_G, pos, with_labels=True)

is_planar, _ = nx.check_planarity(new_G, counterexample=False)
print(is_planar)

nx.is_chordal(new_G)