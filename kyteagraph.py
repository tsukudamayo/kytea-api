import io
import os
import base64
from collections import defaultdict

import numpy as np
import pandas as pd
# from PIL import Image, ImageDraw, ImageFont
from sklearn.externals import joblib


_LOG_DIR = 'C:/Users/tsukuda/var/data/recipe/weekcook/test/ner_result'
_LIKELIFOOD_CSV = 'C:/Users/tsukuda/var/data/recipe/weekcook/test/likelihood/likelihood.csv'
_RNE_MAP = 'rne_category.txt'


def parse_dependency(likelihood, word_order, word_to_rne_map,
                     rne_to_num_map, num_to_rne_map, rne_to_word_map,):
    dependency_list = []
    for idx, word_t in enumerate(word_order):
        print('++++++++++++++++++++++++++++++++')
        print(idx, word_t)
        print('++++++++++++++++++++++++++++++++')
        print(word_t[1] in word_to_rne_map)
        if str(word_t[1]) not in word_to_rne_map:
            print('{} is not exists in rne dictionary'.format(word_t[1]))
            continue
        rne_tag = word_to_rne_map[word_t[1]]
        tag_likelihood_column = rne_to_num_map[rne_tag[0]]
        print('rne_tag', rne_tag[0])
        print('tag_likelihood_column', tag_likelihood_column)
        rne_argmax_tag = rne_argmax(
            word_t[1],
            rne_tag[0],
            likelihood,
            rne_to_num_map,
        )
        print('rne_argmax_tag', rne_argmax_tag)
        dependency_tag = num_to_rne_map[rne_argmax_tag]
        print('dependecy_tag', dependency_tag)
        dependency_candidate = rne_to_word_map[dependency_tag]
        print(dependency_candidate)

        compare_dependency = []
        for order in list(word_order):
            for d_word in dependency_candidate:
                if idx >= order[0]:
                    # print(idx)
                    # print(order[0])
                    # print('big')
                    pass
                else:
                    if d_word in order:
                        compare_dependency.append(order)
                        dependency_word = sorted(compare_dependency)[0][1]
                        print('dependency_word')
                        print(dependency_word)
                    else:
                        pass
        if len(compare_dependency) != 0:
            candidate_agent = sorted(compare_dependency)[0]
            # for duplicating words
            agent_join_word = str(word_t[0]) + '-' + str(word_t[1])
            targs_join_word = str(candidate_agent[0]) + '-' + str(candidate_agent[1])
            dependency_tuple = (agent_join_word, targs_join_word)
            dependency_list.append(dependency_tuple)
        else:
            pass
        # print(dependency_list)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(dependency_list)

    return dependency_list


def load_likelihood(likelihood_csv, index_list):
    print('**************** read loglikelihood data ****************')    
    likelihood = pd.read_csv(likelihood_csv, index_col=0)
    likelihood = pd.concat([likelihood, index_list], axis=1)
    likelihood = likelihood.set_index('index')
    print(likelihood.head())

    return likelihood


def rne_probability(word, tag, likelihood, rne_map):
    tag_id = rne_map[tag]
    probability = max(likelihood[str(tag_id)])

    return probability


def rne_argmax(word, tag, likelihood, rne_map):
    tag_id = rne_map[tag]
    rne_argmax = likelihood[str(tag_id)].idxmax()

    return rne_argmax


def rne_to_num(filepath):
    rne_to_num_map = {}
    with open(filepath, 'r', encoding='utf-8') as r:
        lines = r.readlines()
    for line in lines:
        line = line.rstrip('\n')
        line = line.split(':')
        rne_to_num_map.update({line[1]: int(line[0])})

    return rne_to_num_map


def num_to_rne(filepath):
    num_to_rne_map = {}
    with open(filepath, 'r', encoding='utf-8') as r:
        lines = r.readlines()
    for line in lines:
        line = line.rstrip('\n')
        line = line.split(':')
        num_to_rne_map.update({int(line[0]): line[1]})

    return num_to_rne_map


def word_to_order(strings):
    ordered_list = []
    count = 0
    lines = strings.split('\n')
    for line in lines:
        line = line.rstrip('\n')
        line = line.split(' ')
        for word in line:
            word = word.split('/')
            current_data = (count, word[0])
            ordered_list.append(current_data)
            count += 1

    return ordered_list


def word_to_rne(strings):
    word_to_rne_map = defaultdict(list)
    lines = strings.split('\n')
    for line in lines:
        line = line.split(' ')
        for word in line:
            word = word.split('/')
            print(word)
            if len(word) >= 2:
                print(word)
                if word[1].find('\n') >= 0: # corresponding '。' error
                    word[1] = word[1].replace('\n', '')
                else:
                    pass
                word_to_rne_map[word[0]].append(word[1])
            else:
                pass

    return word_to_rne_map


def rne_to_word(strings):
    rne_to_word_map = defaultdict(list)
    lines = strings.split('\n')
    for line in lines:
        line = line.split(' ')
        for word in line:
            word = word.split('/')
            print(word)
            if len(word) >= 2:
                print(word)
                if word[1].find('\n') >= 0:# corresponding '。' error
                    word[1] = word[1].replace('\n', '')
                rne_to_word_map[word[1]].append(word[0])
            else:
                pass

    return rne_to_word_map


def evaluate_arcs(dependency_list, word_to_id, clf, matrix, prediction_map):
    eval_data = []
    for pair in dependency_list:
        word_pair = []
        for word in pair:
            word = word.split('-')[1]
            if word.find('=') >= 0:
                word = word.split('=')[0]
            print(word)
            word_pair.append(word)
        word_pair = tuple(word_pair)
        eval_data.append(word_pair)
    print('eval_data')
    print(eval_data)

    word_to_id = joblib.load(word_to_id)
    clf = joblib.load(clf)
    matrix = joblib.load(matrix)
    prediction_map = joblib.load(prediction_map)
    all_feature = None
    print('word_to_id : ', word_to_id)
    for path in eval_data:
        print('path : ', path)
        print('matrix : ', matrix)

        # -------------------------- #
        # TODO KeyError Unkown words #
        # -------------------------- #
        try:
            id_1 = word_to_id[path[0]]
            feature_1 = matrix[id_1]
        except KeyError:
            feature_1 = np.ones(matrix.shape[0])
        try:
            id_2 = word_to_id[path[1]]
            feature_2 = matrix[id_2]
        except KeyError:
            feature_2 = np.ones(matrix.shape[0])

        current_feature = np.hstack((feature_1, feature_2))
        if all_feature is None:
            all_feature = current_feature
            all_feature = all_feature[np.newaxis, :]
        else:
            all_feature = np.vstack((all_feature, current_feature))

    print('**************** evaluation ****************')
    print(all_feature.shape)
    print(clf.predict(all_feature))
    pred = clf.predict(all_feature)
    arc_tag_list = np.array([prediction_map[x] for x in pred])
    print(arc_tag_list)

    return arc_tag_list


# # use graphviz
# def output_flowgraph(dependency_list):
#     dst_dir = os.path.join(os.path.dirname(__file__), 'static/flowgraph/assets/img')
#     G = Digraph(format='png')
#     G.attr('node', shape='square', style='filled', fontname='MS Gothic')
#     for pair in dependency_list:
#         print(pair)
#         G.edge(pair[0], pair[1])
#     G.render(os.path.join(dst_dir, 'flowgraph'))

#     return


# # use matplotlib
# def output_flowgraph(dependency_list):
#     plt.rcParams['font.family'] = 'IPAexGothic'
#     plt.figure(figsize=(15, 10))
#     dst_dir = os.path.join(os.path.dirname(__file__), 'static/flowgraph/assets/img')
#     G = nx.DiGraph()
#     for pair in dependency_list:
#         print(pair)
#         G.add_path([pair[0], pair[1]])
#     nx.draw_networkx(
#         G,
#         node_size=2000,
#         node_color='gray',
#         font_family='IPAexGothic',
#     )
#     plt.tight_layout()
#     plt.tick_params(
#         labelbottom=False,
#         labelleft=False,
#         labelright=False,
#         labeltop=False,
#         bottom=False,
#         left=False,
#         right=False,
#         top=False,
#     )
#     plt.savefig(os.path.join(dst_dir, 'flowgraph.png'))

#     return


# def generate_all_node_list(dependency_list):
#     tmp_word = dependency_list[0][1]
#     all_nodes_list = []
#     tmp_node_list = []
#     for i in dependency_list:
#         print(i[0])
#         print(i[1])
#         if i[1] == tmp_word:
#             print('same')
#             tmp_node_list.append(i[0])
#         else:
#             all_nodes_list.append(tmp_node_list)
#             tmp_node_list = []
#             tmp_node_list.append(i[0])
#         tmp_word = i[1]
#         print('tmp_node_list')
#         print(tmp_node_list)
#     # append root word
#     last_word = []
#     last_word.append(tmp_word)
#     all_nodes_list.append(tmp_node_list)
#     all_nodes_list.append(last_word)

#     return all_nodes_list


# def layout_coordinates(height_interval, width_interval, all_nodes_list):
#     y_coord = height_interval
#     xy_coords = []
#     for y in all_nodes_list:
#         tmp_coords = []
#         all_width_list_length = len(y) + 2
#         all_x_list_length = len(y) + 2
#         x_coord = width_interval
#         width_xcoords =\
#           sorted([int(width_interval * w) for w in range(1, all_x_list_length - 1)])
#         for idx, x in enumerate(y):
#             coord = (x_coord, y_coord)
#             tmp_coords.append(coord)
#             x_coord += width_interval
#         xy_coords.append(tmp_coords)
#         y_coord += height_interval

#     return xy_coords


# def render_graph(d, xy_coords, all_nodes_list, graph_size):
#     tmp_start_coord = None
#     drawing_coords_list = []
#     node_start_list = []
#     node_end_list = []
#     for idx1, line in enumerate(xy_coords):
#         print(line)
#         for idx2, c in enumerate(line):
#             start_coord = tuple(c)
#             end_coord = [c[0]+graph_size, c[1]+graph_size]
#             end_coord = tuple(end_coord)

#             output_coords = [start_coord, end_coord]
#             output_coords = tuple(output_coords)

#             try:
#                 node_start_list.append(end_coord)
#                 node_end_list.append(tmp_start_coord)
#             except TypeError:
#                 print('tmp_start_coord is None')
#                 pass

#             d.rectangle(output_coords, fill='gray', width=3)
#             d.text(start_coord, all_nodes_list[idx1][idx2], (0,0,0))
#             # # draw line

#             tmp_start_coord = start_coord

#     return


# def render_edge(d, dependency_list, graph_coords_map):
#     drawing_coords_list = []
#     for depend in dependency_list:
#         n_start = depend[0]
#         n_end = depend[1]
#         print(n_start, n_end)
#         print(graph_coords_map[n_start])
#         print(graph_coords_map[n_end])
#         c1 = graph_coords_map[n_start]
#         c2 = graph_coords_map[n_end]
#         x1 = c2[0][0]
#         x2 = c2[0][1]
#         y1 = c1[1][0]
#         y2 = c1[1][1]
#         drawing_coords = [y1, y2, x1, x2]
#         drawing_coords_list.append(drawing_coords)
#         print('drawing_coords')
#         print(drawing_coords)
#         d.line(tuple(drawing_coords), fill=(0, 0, 0), width=5)

#     return


# def render_arc_tag(d, dependency_list, graph_coords_map, arc_tag_list):
#     drawing_coords_list = []
#     for depend, arc in zip(dependency_list, arc_tag_list):
#         n_start = depend[0]
#         n_end = depend[1]
#         print(n_start, n_end)
#         print(graph_coords_map[n_start])
#         print(graph_coords_map[n_end])
#         c1 = graph_coords_map[n_start]
#         c2 = graph_coords_map[n_end]
#         x1 = c2[0][0]
#         x2 = c2[0][1]
#         y1 = c1[1][0]
#         y2 = c1[1][1]
#         arc_coords = [int((y1+x1)/2), int((y2+x2)/2)]
#         arc_coords = tuple(arc_coords)
#         print('arc_coords')
#         print(arc_coords)
#         d.text(arc_coords, arc, (255, 0, 0))

#     return


# def output_flowgraph(dependency_list, arc_tag_list):
#     dst_dir = os.path.join(os.path.dirname(__file__), 'static/flowgraph/assets/img')
#     height_interval = 200
#     width_interval = 200
#     graph_size = 100  # size of Vertex
#     print('dependency_list')
#     print(dependency_list)

#     # ------------------------
#     # generate all node list
#     # ------------------------
#     all_nodes_list = generate_all_node_list(dependency_list)
#     print('all_nodes_list')
#     print(all_nodes_list)
#     print(len(all_nodes_list))

#     # ---------------------------
#     # layout coordinates of node
#     # ---------------------------
#     all_nodes_list_length = len(all_nodes_list) + 2
#     print('all_nodes_list length')
#     print(len(all_nodes_list))
#     xy_coords = layout_coordinates(
#         height_interval,
#         width_interval,
#         all_nodes_list,
#     )

#     print('all_nodes_list')
#     print(all_nodes_list)
#     print('xy_coords')
#     print(xy_coords)

#     # -----------------
#     # rendering graph
#     # -----------------
#     max_x_length = max([len(x) for x in all_nodes_list]) + 2
#     image_height = width_interval * max_x_length
#     image_width = height_interval * all_nodes_list_length
#     print('image property')
#     print(max_x_length)
#     print(image_height)
#     print(image_width)
#     img = Image.new('RGBA', (image_height, image_width), 'white')
#     d = ImageDraw.Draw(img)
#     font_path = os.path.join(
#         os.path.dirname(__file__), 'ipaexg.ttf'
#     )
#     d.font = ImageFont.truetype(font_path, 25)
#     print('***** xy_coords *****')
#     print('**************** rendering entity and graph ****************')
#     graph_coords_map = defaultdict(list)
#     for x, y in zip(all_nodes_list, xy_coords):
#         current_graph_coords = []
#         for j, k in zip(x, y):
#             coord1 = tuple(k)
#             coord2 = (k[0] + graph_size, k[1] + graph_size)
#             coord_list = [coord1, coord2]
#             graph_coords_map[j].append(coord1)
#             graph_coords_map[j].append(coord2)
#     print('graph_coords_map')
#     print(graph_coords_map)

#     render_graph(d, xy_coords, all_nodes_list, graph_size)
#     render_edge(d, dependency_list, graph_coords_map)
#     if arc_tag_list is not None:
#         render_arc_tag(d, dependency_list, graph_coords_map, arc_tag_list)
#     else:
#         pass

#     img.save(os.path.join(dst_dir, 'flowgraph.png'))
#     buf = io.BytesIO()
#     img.save(buf, format='PNG')
#     base64img = base64.b64encode(buf.getvalue()).decode()
#     # print('base64img')
#     # print(base64img)

#     return base64img


def main():
    # likelifood data config
    index = [0, 2, 4, 5, 8]
    index_list = pd.DataFrame({
        'index': index,
    })
    likelihood = load_likelihood(_LIKELIFOOD_CSV, index_list)

    read_file = os.path.join(_LOG_DIR, 'test_00000002_ner_result.txt')

    print('**************** rne_to_num_map ****************')
    rne_to_num_map = rne_to_num(_RNE_MAP)
    print(rne_to_num_map)

    print('**************** num_to_rne_map ****************')
    num_to_rne_map = num_to_rne(_RNE_MAP)
    print(num_to_rne_map)

    print('**************** word_to_order ****************')
    word_order = word_to_order(read_file)
    print(word_order)

    print('**************** rne_word_map ****************')
    word_to_rne_map = word_to_rne(read_file)
    print('rne_word_map')
    print(word_to_rne_map)

    print('**************** rne_word_map ****************')
    rne_to_word_map = rne_to_word(read_file)
    print('rne_word_map')
    print(rne_to_word_map)

    dependency_list = parse_dependency(
        likelihood,
        word_order,
        word_to_rne_map,
        rne_to_num_map,
        num_to_rne_map,
        rne_to_word_map,
    )
    print('dependency_list')
    print(dependency_list)

    print('################ original file ################')
    with open(read_file, 'r', encoding='utf-8') as read_f:
        lines = read_f.readlines()
    print(lines)
    print('################ dependencies ################')
    print(dependency_list)

    output_flowgraph(dependency_list)


if __name__ == '__main__':
    main()
