import json
import base64
import boto3
import random
from datetime import date
import datetime
from botocore.client import Config
import logging
import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
from datetime import date
import datetime
from pathlib import Path
import networkx as nx
import io
#from PIL import Image
from test_input import test_input_graph_data as test_input
#import geos
#from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from functions import *
from REL_formation import initialize_good_vertices, contract, get_trivial_rel, expand
from REL_to_coord import get_t_neighbors, update_cw_ccw, traverse_face, contains_face, set_node_face, create_face_graph, get_face_num, set_card_node_height, set_card_node_width, set_height, set_width
from FourCompletion import add_nesw_vertices
from triangulation import triangulate_MCSM
from triang_ST_cip import find_non_pyramid_ST, detect_ST, choose_random_edge_from_path, remove_ST
from Visualize_dual_rel import dict_room_color
from Visualization import *

s3 = boto3.client('s3')


def remove_extra_cip(G):
    _, outer_Boundary, _, _ = find_inner_outer(G)
    cip = find_all_CIP(G)
    new_G = G.copy()
    added_nodes_remove_cip = []
    while len(cip) > 4:
        # remove a shortcut
        shortcut = random.choice(find_shortcuts(new_G)[0])
        # print(shortcut)
        new_G, added_node_info = remove_shortcut(new_G.copy(), shortcut)
        added_nodes_remove_cip.append(added_node_info)
        cip = find_all_CIP(new_G)
    return new_G, added_nodes_remove_cip


def remove_all_st(G):
    added_nodes_ST = []
    # we can loop the process to remove multiple ST
    noST_G = G.copy()
    while has_ST(noST_G) == True:
        #sphinx = findST(noST_G)
        sphinx = detect_ST(noST_G)

        if len(sphinx) == 0:
            sphinx = find_non_pyramid_ST(noST_G)[0]
            top, edge, extra_points = sphinx
        else:
            sphinx = sphinx[0]
            top, base = sphinx
            edge, extra_points = choose_random_edge_from_path(
                noST_G, base, top=[top])

        pointA, pointB = edge
        sep_triangle = [top, pointA, pointB, extra_points]
        noST_G, added_node = remove_ST(noST_G, sep_triangle)
        added_nodes_ST.append([added_node, edge])
    return noST_G, added_nodes_ST


def edge_contraction(G):
    good_verts = initialize_good_vertices(G)
    v, u, contracted_G, list_contraction, good_verts = contract(
        G, [], good_verts)

    while v != -1:
        good_verts = initialize_good_vertices(contracted_G)
        v, u, contracted_G, list_contraction, good_verts = contract(
            contracted_G, list_contraction, good_verts)

    return contracted_G, list_contraction


def create_trivial_rel(G):
    trivial_REL_G = get_trivial_rel(G)  # contracted_G
    trivial_REL_G.add_edge("n", "w", t=0)
    trivial_REL_G.add_edge("w", "n", t=0)
    trivial_REL_G.add_edge("n", "e", t=0)
    trivial_REL_G.add_edge("e", "n", t=0)
    trivial_REL_G.add_edge("s", "w", t=0)
    trivial_REL_G.add_edge("w", "s", t=0)
    trivial_REL_G.add_edge("s", "e", t=0)
    trivial_REL_G.add_edge("e", "s", t=0)

    return trivial_REL_G


def edge_expansion(G, list_contraction):
    REL_G = G.copy()
    contractions_list = list_contraction.copy()
    while len(contractions_list) != 0:
        REL_G = expand(REL_G, contractions_list)

    return REL_G


def create_T1_T2(REL_G):
    red = [e for e in list(REL_G.edges) if REL_G[e[0]][e[1]]["t"] == 2]
    blue = [e for e in list(REL_G.edges) if REL_G[e[0]][e[1]]["t"] == 1]
    T1 = REL_G.copy()
    T1.remove_edges_from(red)
    T1.remove_edge("w", "s")
    T1.remove_edge("n", "w")
    T1.remove_edge("e", "s")
    T1.remove_edge("n", "e")

    T2 = REL_G.copy()
    T2.remove_edges_from(blue)
    T2.remove_edge("s", "w")
    T2.remove_edge("n", "w")
    T2.remove_edge("e", "s")
    T2.remove_edge("e", "n")

    return T1, T2


def create_dict_rel(REL_G, T1, T2):
    dict_rel = {"T1": {n: {} for n in list(T1.nodes)}, "T2": {
        n: {} for n in list(T2.nodes)}}
    for n in list(REL_G.nodes):
        dict_rel["T1"][n]['neighbors_cw'] = get_t_neighbors(REL_G, T1, n, t=1)
        dict_rel["T2"][n]['neighbors_cw'] = get_t_neighbors(REL_G, T2, n, t=2)
    update_cw_ccw(dict_rel)
    T1_f = define_T1_faces(dict_rel, T1)
    T2_f = define_T2_faces(dict_rel, T2)
    #print("T1 face:", T1_f)
    #print("T2 face:", T2_f)
    set_node_face(dict_rel, [T1, T2])
    face_dict = create_face_dict(T1_f, T2_f)
    G1 = create_face_graph(T1, dict_rel, face_dict, T="T1")
    G2 = create_face_graph(T2, dict_rel, face_dict, T="T2")

    return dict_rel, face_dict, G1, G2


def create_face_dict(T1_faces, T2_faces):
    faces = {"T1":{}, "T2":{}}
    #print("before:", T1_faces)
    T1_faces = sort_faces(T1_faces, 's', 'n')
    #print("after:", T1_faces)
    #print("before:", T2_faces)
    T2_faces = sort_faces(T2_faces, 'w', 'e')
    #print("after:", T2_faces)

    i = 0
    if 'e' in T1_faces[0] : T1_faces = T1_faces[::-1]
    for face in T1_faces:
        faces["T1"][tuple(face)] = i
        #faces["T1"][i] = tuple(face)
        i += 1
        #break

    i = 0
    if 'n' in T2_faces[0] : T2_faces = T2_faces[::-1]
    for face in T2_faces:
        faces["T2"][tuple(face)] = i
        #faces["T2"][i] = tuple(face)
        i += 1
    #print()
    #print(faces["T1"])
    #print()
    #print(faces["T2"])
    return faces


def define_T1_faces(dict_rel, T1):
    T1_faces = []
    f = traverse_face(dict_rel["T1"], 's', 'n')
    dict_rel["T1"]['s']['w']["left"] = f
    dict_rel["T1"]['w']['n']["left"] = f
    T1_faces.append(list(set(f)))
    for e in list(T1.edges):
        # print(e)
        f = traverse_face(dict_rel["T1"], e[0], e[1])
        #print(e, "face", f)
        ##print(e, f)
        final_face = contains_face(f, T1_faces)
        ##print(f, final_face)
        for j in range(len(final_face)):
            k = (j+1) % len(final_face)
            h = (j-1) % len(final_face)
            e_right = [final_face[j], final_face[k]]
            e_left = [final_face[j], final_face[h]]
            # if T1.has_edge()
            # print(e_right)
            dict_rel["T1"][e_right[0]][e_right[1]]["right"] = final_face
            dict_rel["T1"][e_left[0]][e_left[1]]["left"] = final_face

        if final_face == f:
            T1_faces.append(final_face)

    edge = ('s', 'n')
    dict_rel["T1"][edge[0]][edge[1]]["right"] = dict_rel["T1"]['s']['w']["left"]
    dict_rel["T1"][edge[0]][edge[1]]["left"] = dict_rel["T1"]['s']['e']["right"]
    return T1_faces


def define_T2_faces(dict_rel, T2):
    T2_faces = []
    f = traverse_face(dict_rel["T2"], 'w', 'e')
    dict_rel["T2"]['w']['n']["top"] = f
    dict_rel["T2"]['n']['e']["top"] = f
    T2_faces.append(list(set(f)))
    for e in list(T2.edges):
        f = traverse_face(dict_rel["T2"], e[0], e[1])
        #print(e, f)
        final_face = contains_face(f, T2_faces)
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
    return T2_faces


def define_coordinates(dict_rel, faces, T1, T2, G1, G2):
    exterior_nodes = ["n", "e", "s", "w"]
    rightFace = get_face_num(dict_rel["T1"]['s']['n']["right"], faces["T1"])
    leftFace = get_face_num(dict_rel["T1"]['s']['n']["left"], faces["T1"])

    set_card_node_width(dict_rel, G1, rightFace, leftFace)
    for node in list(T1.nodes):
        if node not in exterior_nodes:
            set_width(node, G1, faces, dict_rel, rightFace)

    botFace = get_face_num(dict_rel["T2"]['w']['e']["bot"], faces["T2"])
    topFace = get_face_num(dict_rel["T2"]['w']['e']["top"], faces["T2"])
    ##print(botFace, topFace)

    set_card_node_height(dict_rel, G2, botFace, topFace)
    for node in list(T2.nodes):
        if node not in exterior_nodes:
            set_height(node, G2, faces, dict_rel, topFace)


def create_room_coord_list(G, REL_G, dict_rel):
    exterior_nodes = ["n", "e", "s", "w"]
    room_list = []
    non_card_nodes = set(list(REL_G.nodes)) - set(exterior_nodes)
    node_list = sorted(non_card_nodes, key = lambda x: int(x)) + exterior_nodes

    for room in node_list:
        if room not in exterior_nodes: #and room in list(G.nodes):
            #print(room)
            x_left,x_right = dict_rel['T1'][room]['x_left'], dict_rel['T1'][room]['x_right']
            y_high,y_low = dict_rel['T2'][room]['y_top'], dict_rel['T2'][room]['y_bot']
            
            coords = [(x_left,y_low), (x_right,y_low), (x_right,y_high), (x_left,y_high)]
            #print(coords)
            room_list.append(coords)
    #print(room_list)
    return room_list


def create_polygon_dict(room_list):
    your_dict = {}

    for i, sublist in enumerate(room_list):

        your_dict[i] = sublist #Polygon(sublist)
    return your_dict

def save_plan_image(G, your_dict, added_nodes_ST, sorted_lines, side_to_annotate, test=True):
    scale = 10
    fig, axs = plt.subplots(figsize=(10,10))
    axs.set_aspect('equal', 'datalim')
    added_nodes_ST_clean = [edge[0] for edge in added_nodes_ST]

    for key,geom in your_dict.items(): 
        xs, ys = [coord[0]*scale for coord in geom], [coord[1]*scale for coord in geom] 
        room_to_append = []
        og_room = key + 1
        key_name = key + 1
        #print("k:", key)
        if key > len(list(G.nodes))-1: 
            if str(key+1) in added_nodes_ST_clean:
                for node_info in added_nodes_ST:
                    if str(key+1) == node_info[0]:
                        room_to_append = [r for r in node_info[1]]
                        index_room = random.randint(0, len(room_to_append)-1)
                        key = int(room_to_append[index_room])
                        print(og_room, index_room)
                        key_name = key
                        break
                else:
                    key = 'extra' 
        else: key = key + 1 
        if key != 'extra':
            color = dict_room_color[str(key)]
            c = [col/255 for col in list(color)]
            if key == 'extra': c = [0.8,0.8,0.8]
            #print(color, c) 
            axs.fill(xs, ys, alpha=0.5, fc=list(c))
            #print(xs, ys)
            axs.text(xs[0]+0.1, ys[0]+0.1, key_name ,fontsize='medium', va='bottom', fontfamily='serif')
            for side in scale_lines(side_to_annotate[str(og_room)], scale):
                annotate_dim(axs,side[0],side[1])

    #print(sorted_lines)
    lines = scale_lines(sorted_lines, scale)
    #print(lines)

    c = [(0,0,0) for line in lines]

    lc = mc.LineCollection(lines, colors=c, linewidths=2)
    axs.add_collection(lc)

    plt.axis('off')
    if test == False:
        # save image as byte object
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        # you will have to fetch the image from this bucket wherever you need th image data/path in other functions
        day = str(date.today())
        now = datetime.datetime.now()
        path = "output/" + day + "/" + str(now.time()) + "/" + "generated_image.png"
        s3.upload_fileobj(img_bytes, "plan-output-temp", path)
        resource = boto3.resource("s3")
        object = resource.Object("plan-output-temp", path)
        object.copy_from(CopySource={'Bucket': "plan-output-temp",
                                'Key': path},
                    MetadataDirective="REPLACE",
                    ContentType="image")
    else:
        num = random.randint(0,2000)
        plt.savefig('test_'+str(num)+".png")
        
    return path


def create_plan_image(your_dict, test=True):
    #return "plan created", your_dict
    fig, axs = plt.subplots()
    axs.set_aspect('equal', 'datalim')
    axs.axis('off')

    for key, geom in your_dict.items():
        xs, ys = [coord[0] for coord in geom], [coord[1] for coord in geom] #geom.exterior.xy
        #key = key + 1
        key_name = key + 1
        if key > 7:
            key = 'extra'
        else:
            key = key + 1
        # if key not in list(dict_room_color.keys()):
          #key = 'extra'
        color = dict_room_color[str(key)]
        c = [col/255 for col in list(color)]
        if key == 'extra':
            c = [0.8, 0.8, 0.8]
        ##print(color, c)
        axs.fill(xs, ys, alpha=0.5, fc=list(c), ec='black')
        ##print(xs, ys)
        axs.text(xs[0]+0.1, ys[0]+0.1, key_name, fontsize='medium',
                 va='bottom', fontfamily='serif')
    plt.axis('off')
    #image_path = os.environ['MPLCONFIGDIR'] + '/plan.png'
    #plt.savefig(image_path)
    
    #saving image to an alternative s3 bucket
    
    if test == False:
        # save image as byte object
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        # you will have to fetch the image from this bucket wherever you need th image data/path in other functions
        day = str(date.today())
        now = datetime.datetime.now()
        path = "output/" + day + "/" + str(now.time()) + "/" + "generated_image.png"
        s3.upload_fileobj(img_bytes, "plan-output-temp", path)
        resource = boto3.resource("s3")
        object = resource.Object("plan-output-temp", path)
        object.copy_from(CopySource={'Bucket': "plan-output-temp",
                                'Key': path},
                    MetadataDirective="REPLACE",
                    ContentType="image")
    else:
        num = random.randint(0,2000)
        plt.savefig('test_'+str(num)+".png")

    return path, your_dict


def create_plan(input_graph_data):
    G = nx.Graph()  # create empty grpah
    # add nodes from the rooms dictionary
    G.add_nodes_from([(str(input_graph_data[key]["adj_ref"]), input_graph_data[key])
                      for key in input_graph_data if key not in ['adjs', "land", "envelope"]])
    adjacencies = [[str(p[0]), str(p[1])] for p in input_graph_data['adjs']]
    G.add_edges_from(adjacencies)

    biconnect_augment_G, added_edges_bicon = biconnect(G.copy())
    triangular_G, added_edges_triang = triangulate_MCSM(
        biconnect_augment_G, randomized=False, reduce_graph=False)["H"]

    noST_G, added_nodes_ST = remove_all_st(triangular_G)
    new_G, added_nodes_cip = remove_extra_cip(noST_G)

    final_added_edges = list(added_edges_triang) + list(added_edges_bicon)
    #print(final_added_edges)

    PTP_G = new_G.copy()
    for e in sorted(final_added_edges):
        PTP_G = transform(PTP_G, e)

    four_G, card_dir_outer = add_nesw_vertices(PTP_G)
    pos = {"1":[0.2,0.8], "2":[-1.2,0 ], "3":[-1.5,-1], "4":[-2,0], "5":[1,0], "6":[-0.1,-1], "7":[0.3, -2], 
       "8":[1.5,-1], "9":[0.5,-1], "10": [-1,0.6], "11": [1.3,0.8], "12": [-0.8,-1],
       "13": [2.5,-0.5], "n": [0.2,2],"e": [ -3,0],"s": [0,-3],"w": [4,0]}
    
    #print(list(four_G.nodes))
    #nx.draw(four_G, pos,  with_labels=True)

    contracted_four_G, contractions = edge_contraction(four_G)
    trivial_rel = create_trivial_rel(contracted_four_G)

    rel_G = edge_expansion(trivial_rel, contractions)

    T1, T2 = create_T1_T2(rel_G)

    dict_rel, face_dict, G1, G2 = create_dict_rel(rel_G, T1, T2)

    #print(dict_rel)

    define_coordinates(dict_rel, face_dict, T1, T2, G1, G2)

    room_coord_list = create_room_coord_list(G, rel_G, dict_rel)
    polygon_dict = create_polygon_dict(room_coord_list)

    bucket_path, image_data = create_plan_image(polygon_dict)

    sorted_lines = get_outside_lines()

    bucket_path = save_plan_image(G, image_data, added_nodes_ST, sorted_lines, side_to_annotate, test=False)

    return bucket_path, image_data, 


s3 = boto3.client('s3')

def lambda_handler(event, context):
    designs = []
    bucket_path, room_pos = create_plan(event["userData"]["constraints"]["1"])
    day = str(date.today())
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    path = "userData/" + day + "/" + event["userData"]["userID"] + "/" + str(now.time()) + "/" + "generated_image.png"
    #s3.upload_file(image_path, "maket-generatedcontent", path)
    #output = "https://maket-generatedcontent.s3.ca-central-1.amazonaws.com/" + path
    #designs.append(output)
    #designs.append(output)
    s3.copy({"Bucket": "plan-output-temp", "Key": bucket_path}, "maket-generatedcontent", path)
    output = "https://maket-generatedcontent.s3.ca-central-1.amazonaws.com/" + path
    designs.append(output)
    designs.append(output)
    designs.append(output)
    designs.append(output)
    designs.append(output)
    designs.append(output)
    return {
        'statusCode': 200,
        'userData': event["userData"]["userID"],
        'designs': designs
    }


bucket_path, room_pos = create_plan(test_input["userData"]["constraints"]["1"])