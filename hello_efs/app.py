import json
import base64
import boto3
import json
from datetime import date
import datetime
from pathlib import Path
import networkx as nx
import random
from PIL import Image
from test_input import test_input_graph_data as test_input
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from functions import *
from REL_formation import initialize_good_vertices, contract, get_trivial_rel, expand
from REL_to_coord import get_t_neighbors, update_cw_ccw, traverse_face, contains_face, set_node_face, create_face_graph, get_face_num, set_card_node_height, set_card_node_width, set_height, set_width
from FourCompletion import add_nesw_vertices
from triangulation import triangulate_MCSM
from triang_ST_cip import find_non_pyramid_ST, detect_ST, choose_random_edge_from_path, remove_ST
from Visualize_dual_rel import dict_room_color


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
    set_node_face(dict_rel, [T1, T2])
    face_dict = create_face_dict(T1_f, T2_f)
    G1 = create_face_graph(T1, dict_rel, face_dict, T="T1")
    G2 = create_face_graph(T2, dict_rel, face_dict, T="T2")

    return dict_rel, face_dict, G1, G2


def create_face_dict(T1_faces, T2_faces):
    faces = {"T1": {}, "T2": {}}
    i = 1
    while i < len(T1_faces) - 1:
        for face in sorted(T1_faces, key=len):
            # print(i)
            if len(face) == 3 and 'w' in face:
                faces["T1"][tuple(face)] = 0
                faces["T1"][0] = tuple(face)
            elif len(face) == 3 and 'e' in face:
                faces["T1"][tuple(face)] = len(T1_faces) - 1
                faces["T1"][len(T1_faces) - 1] = tuple(face)
            else:
                #inter = set(list(faces["T1"].keys())[list(faces["T1"].values()).index(i-1)]).intersection(set(face))
                # if len(inter) >= 2 and tuple(face) not in faces["T1"]:
                ##print(face, faces["T1"][i-1])
                faces["T1"][tuple(face)] = i
                faces["T1"][i] = tuple(face)
                i += 1
                # break

    i = 1
    while i < len(T2_faces) - 1:
        if i == 6:
            break
        for face in sorted(T2_faces, key=len):
            # print(i)
            if len(face) == 3 and 's' in face:
                faces["T2"][tuple(face)] = 0
                faces["T2"][0] = tuple(face)
            elif len(face) == 3 and 'n' in face:
                faces["T2"][tuple(face)] = len(T2_faces) - 1
                faces["T2"][len(T2_faces) - 1] = tuple(face)
            else:
                #inter = set(list(faces["T2"].keys())[list(faces["T2"].values()).index(i-1)]).intersection(set(face))
                # if len(inter) >= 2: #print(face, faces["T2"][i-1])
                # if len(inter) >= 2 and tuple(face) not in faces["T2"]:
                ##print(face, faces["T2"][i-1])
                faces["T2"][tuple(face)] = i
                faces["T2"][i] = tuple(face)
                i += 1
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
    dict_rel["T1"][edge[0]][edge[1]
                            ]["right"] = dict_rel["T1"]['s']['w']["left"]
    dict_rel["T1"][edge[0]][edge[1]
                            ]["left"] = dict_rel["T1"]['s']['e']["right"]
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

    botFace = get_face_num(dict_rel["T2"]['w']['e']["top"], faces["T2"])
    topFace = get_face_num(dict_rel["T2"]['w']['e']["bot"], faces["T2"])
    ##print(botFace, topFace)

    set_card_node_height(dict_rel, G2, botFace, topFace)
    botFace = get_face_num(dict_rel["T2"]['w']['e']["top"], faces["T2"])
    topFace = get_face_num(dict_rel["T2"]['w']['e']["bot"], faces["T2"])
    ##print(botFace, topFace)

    set_card_node_height(dict_rel, G2, botFace, topFace)
    for node in list(T2.nodes):
        if node not in exterior_nodes:
            set_height(node, G2, faces, dict_rel, botFace)


def create_room_coord_list(G, REL_G, dict_rel):
    exterior_nodes = ["n", "e", "s", "w"]
    room_list = []

    for room in list(REL_G.nodes):

        if room in list(G.nodes):
            color = dict_room_color[room]
        else:
            color = dict_room_color['extra']

        # if room == 'n' or room =='s' or room == 'w' or room=='e' or room=='1':

        if room not in exterior_nodes:  # and room in list(G.nodes):
            # print(room)
            x_left, x_right = dict_rel['T1'][room]['x_left'], dict_rel['T1'][room]['x_right']
            y_high, y_low = dict_rel['T2'][room]['y_top'], dict_rel['T2'][room]['y_bot']
            #x_left,x_right = dict_rel['T2'][room]['y_top'], dict_rel['T2'][room]['y_bot']
            #y_high,y_low = dict_rel['T1'][room]['x_left'], dict_rel['T1'][room]['x_right']

            #print(room, (x_left,x_right), (y_high,y_low), color)
            #w, h = x_right - x_left, y_high - y_low
            coords = [(x_left, y_low), (x_right, y_low),
                      (x_right, y_high), (x_left, y_high)]
            # print(coords)
            room_list.append(coords)
    return room_list


def create_polygon_dict(room_list):
    your_dict = {}

    for i, sublist in enumerate(room_list):

        your_dict[i] = Polygon(sublist)
    return your_dict


def create_plan_image(your_dict):
    fig, axs = plt.subplots()
    axs.set_aspect('equal', 'datalim')
    axs.axis('off')

    for key, geom in your_dict.items():
        xs, ys = geom.exterior.xy
        #key = key + 1
        key_name = key + 1
        if key > 7:
            key = 'extra'
        else:
            key = key + 1
        # if key not in list(dict_room_color.keys()):
          #key = 'extra'
        color = dict_room_color[str(key)]
        c = (color - np.min(color))/np.ptp(color)
        if key == 'extra':
            c = [0.8, 0.8, 0.8]
        ##print(color, c)
        axs.fill(xs, ys, alpha=0.5, fc=list(c), ec='black')
        ##print(xs, ys)
        axs.text(xs[0]+0.1, ys[0]+0.1, key_name, fontsize='medium',
                 va='bottom', fontfamily='serif')
    plt.axis('off')
    #plt.show()
    path = 'plan.png'
    plt.savefig('plan.png')

    #img = Image.open(path)

    #numpydata = np.asarray(img)

    return path, []


def create_plan(input_graph_data):
    G = nx.Graph()  # create empty grpah
    # add nodes from the rooms dictionary
    G.add_nodes_from([(str(key), input_graph_data[key])
                      for key in input_graph_data if key != 'adjs'])
    adjacencies = [[str(p[0]), str(p[1])] for p in input_graph_data['adjs']]
    G.add_edges_from(adjacencies)

    biconnect_augment_G, added_edges_bicon = biconnect(G.copy())
    triangular_G, added_edges_triang = triangulate_MCSM(
        biconnect_augment_G, randomized=False, reduce_graph=False)["H"]

    noST_G, added_nodes_ST = remove_all_st(triangular_G)
    new_G, added_nodes_cip = remove_extra_cip(noST_G)

    final_added_edges = list(added_edges_triang) + list(added_edges_bicon)

    PTP_G = new_G.copy()
    for e in sorted(final_added_edges):
        PTP_G = transform(PTP_G, e)

    four_G, card_dir_outer = add_nesw_vertices(PTP_G)

    contracted_four_G, contractions = edge_contraction(four_G)
    trivial_rel = create_trivial_rel(contracted_four_G)

    rel_G = edge_expansion(trivial_rel, contractions)

    T1, T2 = create_T1_T2(rel_G)

    dict_rel, face_dict, G1, G2 = create_dict_rel(rel_G, T1, T2)

    define_coordinates(dict_rel, face_dict, T1, T2, G1, G2)

    room_coord_list = create_room_coord_list(G, rel_G, dict_rel)
    polygon_dict = create_polygon_dict(room_coord_list)

    plan, image_data = create_plan_image(polygon_dict)

    return plan, image_data


s3 = boto3.client('s3')


def lambda_handler(event, context):
    if event["queryStringParameters"]["sender"] == "0":
        response = s3.get_object(
            Bucket='maket-generatedcontent',
            Key='userData/2022-07-07/jessen/21:15:00/2D_design.png',
        )
        image = response['Body'].read()

        return {
            'headers': {"Content-Type": "image/png"},
            'statusCode': 200,
            'body': base64.b64encode(image).decode('utf-8'),
            'isBase64Encoded': True
        }
    else:
        # create image
        plan_file, image_data = create_plan(test_input)
        # write image to user specific s3 container
        day = str(date.today())
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        path = "userData/" + day + "/" + \
            event["queryStringParameters"]["sender"] + "/" + \
            str(now.time()) + "/" + "generated_image.png"
        s3.upload_file("./2D_design.png", "maket-generatedcontent", path)
        output = "https://maket-generatedcontent.s3.ca-central-1.amazonaws.com/" + path
        return {
            'body':  json.dumps({
                'headers': {"Content-Type": "application/json"},
                'statusCode': 200,
                "output": output,
                "plan_fn" :  plan_file,
                "img_data" : image_data
            }),

        }


#fn, numpy_image = create_plan(test_input)
