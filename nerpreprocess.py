import sys
import subprocess

import numpy as np

import nesearch as ne

_KBM_MODEL = 'kytea-win-0.4.2/model/jp-0.4.7-1.mod'
_KNM_MODEL = 'kytea-win-0.4.2/RecipeNE-sample/recipe416.knm'
_KYTEA_PATH = 'kytea-win-0.4.2/kytea.exe'


class Finalizer:
    def __init__(self, wakati, ner, org):
        super(Finalizer, self).__init__()
        self.wakati = wakati
        self.ner = ner
        self.m_lists = []
        self.ner_lists = []
        self.org = org

    def result_output(self):
        result = ''
        m_lists_sublist = []
        
        for line in self.wakati.split('\n'):
            print('line1')
            print(line)
            line = line.split(' ')
            # line = line.replace('\n', '').split(' ')
            line = [n for n in line if n]   # delete empty character
            print('line2w')
            print(line)
            # self.m_lists.append(line)
            m_lists_sublist.extend(line)
        self.m_lists.append(m_lists_sublist)

        for line in self.ner.split('\n'):
            line = line.split(' ')
            # line = line.replace('\n', '').split(' ')
            print('line2r')
            print(line)
            self.ner_lists.append(self.modify_viob(line))
        print(self.ner_lists)

        ref_lf_strings = self.org.split('\n')
        print('ref_lf_strings')
        print(ref_lf_strings)
        lf_map = {idx: value for idx, value in enumerate(ref_lf_strings)}
        print('lf_map')
        print(lf_map)

        lf_map_num = 0
        lf_observer = ''
        is_lf = False

        for m_list, ner_list in zip(self.m_lists, self.ner_lists):
            print('restore/m_list')
            print(m_list)
            print('resotre/ner_list')
            print(ner_list)
            restored_list = self.restore(m_list, ner_list)
            print('restored_list')
            print(restored_list)
            output_list = self.join_words(restored_list)
            print('output_list')
            print(output_list)

            for word in output_list:
                if word != '/':
                    observe_word = word.split('/')[0]
                elif word == '/':
                    observe_word = '/'
                observe_word = observe_word.replace('=', '')
                lf_observer += observe_word
                if lf_observer == lf_map[lf_map_num] and is_lf is False:
                    is_lf = True
                if is_lf is True and word == '。':
                    word = '。\n'
                    word += ' '
                    is_lf = False
                    lf_observer = ''
                    lf_map_num += 1
                    result += word
                    continue
                else:
                    pass
                result += word
                result += ' '
            result += '\n'
            # result += ' '.join(output_list) + '\n'

        return result

    def modify_viob(self, input_list):
        output_list = []
        for item in input_list:
            if item == '':
                continue
            item = item.split('/')
            if item[1] == 'O':
                output_list.append(item[0])
            else:
                output_list.append(item[0] + '/' + item[1].split('-')[0])

        return output_list

    def restore(self, morphology_list, ner_list):
        output_list = []
        for m_item, ner_item in zip(morphology_list, ner_list):
            m_item = m_item.split('/')
            if '/' in ner_item and ner_item != '/':
                ner_item = ner_item.split('/')
            elif '/' in ner_item and ner_item == '/':
                ner_item = ['/', '']
                m_item = ['/', '']
            else:
                ner_item = [ner_item, '']
            if m_item[0] != ner_item[0]:
                # debug print
                print('ERROR: m_item != ner_item at restore')
                print('m_item')
                print(m_item[0])
                print('ner_item')
                print(ner_item[0])
                sys.exit()
            if ner_item[0] != '/' and ner_item[1] == '':
                output_list.append(','.join(m_item))
            elif ner_item[0] == '/' and ner_item[1] == '':
                output_list.append('/')
            else:
                output_list.append(','.join(m_item) + '/' + ner_item[1])
        print('output_list')
        print(output_list)

        return output_list

    def join_words(self, input_list):
        tag_list = []
        for item in input_list:
            item = item.split('/')
            if len(item) == 1:
                tag_list.append('')
            else:
                tag_list.append(item[1])
        i = 0
        output_str = ''
        for item in input_list:
            if tag_list[i] == '':
                output_str += item + ' '
            else:
                if i == (len(input_list) - 1):
                    output_str += item + ' '
                else:
                    if tag_list[i] == tag_list[i + 1]:
                        output_str += item.split('/')[0] + '='
                    else:
                        output_str += item + ' '
            i += 1
        output_list = output_str.split(' ')[:-1]

        return output_list


def parse_recipe(text: str, model_path: str, kytea_path: str) -> str:
    print('input text')
    cmd_echo = subprocess.Popen(
        ['echo', text],
        stdout=subprocess.PIPE,
    )
    cmd_kytea = subprocess.Popen(
        [kytea_path, '-model', model_path],
        stdin=cmd_echo.stdout,
        stdout=subprocess.PIPE,
    )
    end_of_pipe = cmd_kytea.communicate()[0].decode('utf-8')

    return end_of_pipe


def insert_space_between_words(text: str) -> str:
    if len(text) == 1:
        pass
    else:
        text = text.replace('\n', ' ')
        words = [w.split('/')[0] if w.count('/') <= 2 else '/' for w in text.split(' ')]
        output = ' '.join(words) + '\n'

    return output


def ner_tagger_1(text: str, model_path: str, kytea_path: str):
    cmd_echo = subprocess.Popen(
        ['echo', text],
        stdout=subprocess.PIPE,
    )
    cmd_kytea = subprocess.Popen(
        [kytea_path, '-model', model_path,
         '-out', 'conf', '-nows',
         '-tagmax', '0', '-unktag', '/UNK'],
        stdin=cmd_echo.stdout,
        stdout=subprocess.PIPE,
    )
    end_of_pipe = cmd_kytea.communicate()[0].decode('utf-8')

    return end_of_pipe


def ner_tagger_2(score: str):
    rnetag_list = np.array(['Ac', 'Af', 'F', 'Sf', 'St', 'Q', 'D', 'T'])

    tag_kinds = np.array([ne.BIOtag_append(tag) for tag in rnetag_list])
    tag_kinds = tag_kinds.flatten()

    head_tag = np.array([ne.genereate_headtag(tag) for tag in tag_kinds])

    tag_kinds = np.append(tag_kinds, ['O'], axis=0)
    head_tag = np.append(head_tag, [1], axis=0)

    connect_matrix = np.array(
        [ne.generate_connection_matrix(tag, tag_kinds) for tag in tag_kinds]
    )

    food_list, tag_list, prob_list = ne.text_to_list(score)

    # --------------------------
    # viterbi forward algorithm
    # --------------------------
    prob_matrix, edge_matrix, prob_history = ne.viterbi_forward(
        food_list,
        tag_list,
        prob_list,
        tag_kinds,
        head_tag,
        connect_matrix
    )

    # --------------------------
    # viterbi forward algorithm
    # --------------------------
    result_rnetag = ne.viterbi_backward(
        tag_kinds,
        food_list,
        prob_matrix,
        edge_matrix
    )

    output = ''
    for word, tag in zip(food_list, result_rnetag):
        output += word
        output += '/'
        output += tag
        output += ' '

    return output
