import os
import sys

import numpy as np

# ---------------
# preprocessing
# ---------------
def BIOtag_append(tag_string):
    btag = tag_string + '-B'
    itag = tag_string + '-I'

    return np.array([btag, itag])


def genereate_headtag(tag_string):
    if tag_string.find('-B') >= 0:
        return 1
    elif tag_string.find('-I') >= 0:
        return 0
    else:
        print('someting wrong', tag_string)
        raise ValueError


def verify_tag_matching(tag_string, search_tag):
    tag_without_bio = search_tag.split('-')[0]
    if tag_string.find(str(tag_without_bio)) >= 0:
        return 1
    else:
        return 0


def is_tag_I_or_B(tag_string):
    if tag_string.find('-I') >= 0:
        return True
    elif tag_string.find('-B') >= 0:
        return False
    else:
        print('something wrong', tag_string)
        raise ValueError


def generate_connection_matrix(tag1, tag_kinds):
    if tag1.find('-B') >= 0 or tag1 == 'O':
        return np.ones(len(tag_kinds))
    else:
        return np.array([verify_tag_matching(tag1, x) for x in tag_kinds])


def split_by_space(strings):
    strings = strings.replace('\r\n', '\n')
    strings = strings.rstrip('\n')
    strings = strings.split(' ')

    return strings


def text_to_list(text):
    food_list = []
    tag_list = []
    prob_list = []

    if os.name == 'nt':
        lines = text.split('\r\n')
    else:
        lines = text.split('\n')

    for line in lines:
        if line.find('&') >= 0 and line.find('/') >= 0:
            line = split_by_space(line)
            for words in line:
                # tsukuda change for /=bugfix
                if words.find('//') >= 0: 
                    food = '/'
                    word = words.split('//')[1]
                    tags = word.split('&')
                    food_list.append(food)
                    tag_list.append(tags)
                elif words.find('/') >= 0:
                    food = words.split('/')[0]
                    word = words.split('/')[1]
                    tags = word.split('&')
                    food_list.append(food)
                    tag_list.append(tags)
        elif line.find('&') >= 0:
            line = split_by_space(line)
            for words in line:
                probs = words.split('&')
                prob_list.append(probs)
        else:
            pass

    return food_list, tag_list, prob_list


# ------------------------------
# decoding by viterbi algorithm
# ------------------------------
def viterbi_forward(food_list, tag_list, prob_list, tag_kinds, head_tag, connect_matrix):
    print('**************** initialize ****************')
    print('food_list')
    print(food_list)
    # -------------
    # initialize
    # -------------
    print('tag_kinds')
    print(tag_kinds)
    print(len(tag_kinds))
    prob_history = []
    tag_probabilities = {}
    all_words_length = range(len(food_list))
    prob_matrix = np.zeros(shape=(len(all_words_length), len(tag_kinds)))
    edge_matrix = np.zeros(shape=(len(all_words_length), len(tag_kinds)))
    tag_prob_hash = {tag: prob for tag, prob in zip(tag_list[0], prob_list[0])}
    print('############## ' + food_list[0] + ' ##############')
    for t in range(len(tag_kinds)):
        prob = tag_prob_hash[tag_kinds[t]]
        current_prob = float(head_tag[t])*float(prob)

        tag_probabilities.update({tag_kinds[t]: float(head_tag[t])*float(prob)})
        # print(tag_probabilities)

        edge_matrix[0][t] = 0
        prob_matrix[0][t] = current_prob

        # -------------------------
        # kytea probability debug
        # -------------------------
        print(
            tag_kinds[t],
            head_tag[t],
            prob,
            head_tag[t]*prob,
        )

    prob_history.append(tag_probabilities)
    # print('prob_history')
    # print(prob_history)

    # -----------------------
    # After the second time
    # -----------------------
    for i in range(1, len(all_words_length)):
        print('tag_kinds')
        print(tag_kinds)
        print(len(tag_kinds))
        print('################################')
        print('i', i)
        print('############## ' + food_list[i] + ' ##############')
        tag_probabilities = {}
        tag_prob_hash = {tag: prob for tag, prob in zip(tag_list[i], prob_list[i])}
        print('tag_prob_hash')
        print(tag_prob_hash)
        for t in range(len(tag_kinds)):
            prob = tag_prob_hash[tag_kinds[t]]
            print(tag_kinds[t], prob)
            tag_probabilities.update({tag_kinds[t]: float(head_tag[t])*float(prob)})

            edge_matrix[i][t] = 0
            prob_matrix[i][t] = float(head_tag[t])*float(prob)

            # -------------------------
            # kytea probability debug
            # -------------------------
            print(
                tag_kinds[t],
                head_tag[t],
                prob,
                head_tag[t]*prob,
            )

        for j in range(len(tag_kinds)):
            for k in range(len(tag_kinds)):
                prev_score = np.array([x for x in prob_history[i - 1].values()])
                prev_max = np.argmax(prev_score)
                tmpprob = prev_max * connect_matrix[j][k] * float(prob)

                if (prob_matrix[i][j] < tmpprob):
                    edge_matrix[i][j] = k

        prob_history.append(tag_probabilities)
    # print(prob_history)

    # for i in prob_history:
    #     print(i)

    # print('connnect_matrix')
    # print(connect_matrix)
    return prob_matrix, edge_matrix, prob_history


def viterbi_backward(tag_kinds, food_list, prob_matrix, edge_matrix):
    # -------------------------------------------------
    # Select tag with maximum probability at last node
    # -------------------------------------------------
    last_node_max_prob = 0
    selected_tag = 0
    for i in range(len(tag_kinds)):
        print(i)
        print(prob_matrix[-1][i])
        if (last_node_max_prob < prob_matrix[-1][i]):
            last_node_max_prob = prob_matrix[-1][i]
            selected_tag = i
        else:
            pass
    # print('last_node_max_prob')
    # print(last_node_max_prob)
    # print('selected_tag')
    # print(selected_tag)
    # print('tag_kinds')
    # print(tag_kinds)


    # ------------
    # backward
    # ------------
    result_tag = []
    first_value = selected_tag
    for i in range(len(food_list) -1, -1, -1):
        edge_index = np.argmax(prob_matrix[i])
        print('**************** edge_index ****************')
        print(edge_index)
        print(int(edge_matrix[i][edge_index]))
        # result_tag.append(int(edge_matrix[i][edge_index]))
        result_tag.append(int(edge_index))
        
    result_tag.insert(0, first_value)
    print(result_tag)
    print('frip')
    print(np.flip(result_tag))
    flip_result_tag = np.flip(result_tag)
    print('flip_result_tag')
    print(flip_result_tag)

    result_rnetag = np.array([tag_kinds[x] for x in flip_result_tag])
    print(result_rnetag)
        
    return result_rnetag


def main():
    # ---------------------------
    # generate connection matrix
    # ---------------------------    
    rnetag_list = np.array(['Ac', 'Af', 'F', 'Sf', 'St', 'Q', 'D', 'T'])

    tag_kinds = np.array([BIOtag_append(tag) for tag in rnetag_list])
    tag_kinds = tag_kinds.flatten()

    head_tag = np.array([genereate_headtag(tag) for tag in tag_kinds])

    # /O tag
    tag_kinds = np.append(tag_kinds, ['O'], axis=0)
    head_tag = np.append(head_tag, [1], axis=0)

    connect_matrix = np.array(
        [generate_connection_matrix(tag, tag_kinds) for tag in tag_kinds]
    )

    # -----
    # test
    # -----
    # print('tag_kinds')
    # print(tag_kinds)

    # print('head_tag')
    # print(head_tag)

    # print('tag_kinds')
    # print(tag_kinds)
    # print('head_tag')
    # print(head_tag)

    # print('connect_matrix')
    # print(connect_matrix)

    # --------------------------------------
    # get result of tag estimation by kytea
    # --------------------------------------
    read_file = sys.argv[1]
    food_list, tag_list, prob_list = text_to_list(read_file)

    # print('foods', food_list)
    # print('tags', tag_list)
    # print('probs', prob_list)

    # ---------------
    # generate hash
    # ---------------
    foods_tags_hash = {food: tag for (food, tag) in zip(food_list, tag_list)}
    # print('foods_tags_hash')
    # print(foods_tags_hash)
    foods_probs_hash = {food: prob for (food, prob) in zip(food_list, prob_list)}
    # print('foods_probs_hash')
    # print(foods_probs_hash)
    foods_number_hash = {i: food for (i, food) in enumerate(food_list)}
    # print('foods_number_hash')
    # print(foods_number_hash)

    # --------------------------
    # viterbi forward algorithm
    # --------------------------
    prob_matrix, edge_matrix = viterbi_forward(
        food_list,
        tag_kinds,
        head_tag,
        connect_matrix,
        foods_tags_hash,
        foods_number_hash,
        foods_probs_hash
    )
    print('**************** prob_matrix ****************')
    for i in prob_matrix:
        print(i)

    print('**************** edge_matrix ****************')
    for i in edge_matrix:
        print(i)

    # --------------------------
    # viterbi forward algorithm
    # --------------------------
    result_rnetag = viterbi_backward(
        tag_kinds,
        food_list,
        prob_matrix,
        edge_matrix
    )
    print('result_rnetag')
    print(result_rnetag)

    # -----------------------
    # result output to text
    # -----------------------
    with open('test.txt', 'w', encoding='utf-8') as w:
        for word, tag in zip(food_list, result_rnetag):
            w.write(word)
            w.write('/')
            w.write(tag)
            w.write(' ')



if __name__ == '__main__':
    main()
