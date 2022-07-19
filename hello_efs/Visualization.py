import matplotlib.pyplot as plt
from matplotlib import collections  as mc
import random
import math
from Visualize_dual_rel import dict_room_color

def rect_to_lines(rect):
  a,b,c,d = rect
  return [[a,b], [b,c], [c,d], [d,a]]

def in_segment(p, s):
  a, b = s
  if p[0] == a[0] and p[0] == b[0] and p[1] >= min(a[1], b[1]) and p[1] <= max(a[1], b[1]):
    return True
  if p[1] == a[1] and p[1] == b[1] and p[0] >= min(a[0], b[0]) and p[0] <= max(a[0], b[0]):
    return True
  return False 

def point_in_rect(p, rectangle):
  if p in rectangle: return True
  a,b,c,d = rectangle
  return in_segment(p, (a,b)) or in_segment(p, (b,c)) or in_segment(p, (c,d)) or in_segment(p, (d,a))

def get_all_points_segment(G, your_dict, added_nodes_ST_clean):
  all_points = []
  all_segment = []
  #unique_segment = []
  for key,geom in your_dict.items(): 
    if str(key+1) in list(G.nodes) + added_nodes_ST_clean:
      #print(key, str(key+1))
      for i, point in enumerate(geom):
        k = i + 1 if i < len(geom)-1 else 0
        #print(i,k)
        all_points.append(point)
        side = [geom[i], geom[k]]
        if side in all_segment:
          all_segment.append(side)
        elif side[::-1] in all_segment:
          all_segment.append(side[::-1])
        else: all_segment.append(side)
  return all_points, all_segment


def get_boundary_points(G, your_dict, all_points, added_nodes_ST_clean):
  boundary_points = []
  for point in all_points:
    count = 0
    for key,geom in your_dict.items():
      if str(key+1) in list(G.nodes) + added_nodes_ST_clean:
        if point_in_rect(point, geom) == True:
          count += 1
          #if point[0] == 7: print(point, geom)
    if count <= 2:
      #print(point)
      if point not in boundary_points: boundary_points.append(point)
  return boundary_points

def get_boundary_lines(all_segment, boundary_points):
  boundary_lines = []
  inside_lines = []
  for side in all_segment:
    p1, p2 = side
    if p1 in boundary_points and p2 in boundary_points and side not in boundary_lines :
      boundary_lines.append(list(side))
    else: inside_lines.append(side)
  return boundary_lines

def get_outside_lines(boundary_lines, boundary_points):
  sorted_lines = []
  points_to_connect = []
  for line in boundary_lines:
    valid = True
    for point in boundary_points:
      if point not in line and in_segment(point, line):
        print(point, line)
        valid = False
        points_to_connect.append(point)
        break
    if valid: sorted_lines.append(line)

def count_line_use(sorted_lines, boundary_points):
  point_use = {p:0 for p in boundary_points}
  for line in sorted_lines:
    if line[0] in point_use:
      point_use[line[0]] += 1
    elif line[0][::-1] in point_use:
      point_use[line[0][::-1]] += 1
    if line[1] in point_use:
      point_use[line[1]] += 1
    elif line[1][::-1] in point_use:
      point_use[line[1][::-1]] += 1
  return point_use
  
def get_side_to_annotate(G, your_dict, sorted_lines, added_nodes_ST_clean):
  side_to_annotate = {n:[] for n in list(G.nodes) + added_nodes_ST_clean}
  for key,geom in your_dict.items(): 
      if str(key+1) in list(G.nodes) + added_nodes_ST_clean:
        for line in rect_to_lines(geom):
          if line in sorted_lines or line[::-1] in sorted_lines:
            side_to_annotate[str(key+1)] += [line]
  return side_to_annotate


def annotate_dim(ax,xyfrom,xyto,text=None):
  offeset_x = 0
  offeset_y = 0
  # vertical line
  if xyfrom[0] == xyto[0]:
    #move to right == increase x
    tmp = xyto[0] + 1
    xyfrom = (tmp, xyfrom[1])
    xyto = (tmp, xyto[1])
  # horizontal line
  if xyfrom[1] == xyto[1]:
    #move up == increase y
    tmp = xyto[1] + 1
    xyfrom = (xyfrom[0], tmp)
    xyto = (xyto[0], tmp)
    offeset_y = 1
    offeset_x = -3

  if text is None:
      text = str(round(math.sqrt( (xyfrom[0]-xyto[0])**2 + (xyfrom[1]-xyto[1])**2 ), 2))

  ax.annotate("",xyfrom,xyto,arrowprops=dict(arrowstyle='<->'))
  ax.text((xyto[0]+xyfrom[0])/2+offeset_x ,(xyto[1]+xyfrom[1])/2+offeset_y,text,fontsize=16)

def scale_lines(line_list, factor):
  scaled_lines = []
  for line in line_list:
    l = []
    for p in line:
      new_p = (p[0]*factor, p[1]*factor)
      l.append(new_p)
    scaled_lines.append(l)
  return scaled_lines