import os
import re
import json


_HOME = os.path.expanduser("~")
_INGREDIENTS_DIR = '../recipe_conv/weekcook/ingredient_json'
_SENTENCES_DIR = './rne_wakachi'
_ACTIONS_DIR = './countAC'
_ACTIONS_CATEGORY_DIR = './action_category'
_RECIPEDB_DIR = os.path.join(_HOME, 'var/data/recipe/weekcook/recipe_root')

_OUTPUT_DIR = './num_of_params'


def count_action_category(action_category: str, wakati_strings: str, category_file: str) -> int:
    category_count = 0
    words = wakati_strings.split(' ')
    print('words', words)

    with open(category_file, 'r', encoding='utf-8') as r:
        data = json.load(r)

    print('action category : ', data)
    for w in words:
        try:
            if data[w] == action_category:
                print(w)
                category_count += 1
            else:
                pass
        except KeyError:
            pass

    return category_count


def count_string_length(strings: str) -> int:
    words = strings.replace(' ', '')
    length = len(words)

    return length


def count_elements(data: dict) -> int:

    return len(data)


def count_lf(text_file: str) -> int:
    strings = open(text_file, 'r', encoding='utf-8').read()
    data = strings.split(' ')

    return data.count('。')


def output_jsondata(*args) -> str:
    print('args', args)
    output = [d for d in args]
    print('output : ', output)

    return json.dumps(output)


def fetch_recipename(json_file: str) -> str:
    with open(json_file, 'r', encoding='utf-8') as r:
        input_data = json.load(r)
        recipe_name = input_data['Recipe_Infos'][0]['recipe_name']
        print(recipe_name)

    return recipe_name


def compute_mean(dict_data: dict) -> float:
    all_value = [v for v in dict_data.values() if type(v) is not str]
    length_all_value = len(all_value)
    mean_value = float(sum(all_value) / length_all_value)

    return mean_value


def compute_max(dict_data: dict) -> float:
    all_value = [v for v in dict_data.values() if type(v) is not str]
    max_value = max(all_value)

    return max_value


def standardization_by_level(dict_data: dict, max_value: float, level: int) -> dict:
    for k in dict_data:
        try:
            dict_data[k] = float(dict_data[k] / max_value) * float(level)
        except TypeError:  # if dict_data[k] is type(str)
            dict_data[k] = dict_data[k]

    return dict_data


def ingredient_list_to_dict(strings: str) -> dict:
    _INDENT = -1 # -1, 0, 1
    lines = strings.split('\n')
    for idx, line in enumerate(lines):

        if line == '':
            del lines[idx]
            continue

        if line[0] == '　' and _INDENT == -1:
            _INDENT = 0
            del lines[idx - 1]
        elif line[0] == '　' and _INDENT == 0:
            _INDENT = 1
        elif line[0] != '　' and _INDENT == 1:
            _INDENT = -1
        else:
            pass

    lines = [re.sub('^　', '', w) for w in lines]
    lines = [re.sub('　$', '', w) for w in lines]
    lines = [w.split('　') for w in lines]

    target_dict = {}
    for line in lines:
        if len(line) != 2:
            target_dict.update({line[0]: ''})
            continue
        target_dict.update({line[0]: line[1]})

    return target_dict


def main():
    if os.path.exists(_OUTPUT_DIR) is False:
        os.makedirs(_OUTPUT_DIR)
    else:
        pass

    file_list = os.listdir(_INGREDIENTS_DIR)

    # ---------------- #
    # define index key #
    # ---------------- #

    # recipe title
    title_dict = {'key': 'recipename'}

    # axis of the radarchart parmeters
    axis1_dict = {'key': 'ingredients'}
    axis2_dict = {'key': 'sentences'}
    axis3_dict = {'key': 'heat'}
    axis4_dict = {'key': 'mix'}
    axis5_dict = {'key': 'cut'}

    # recipe level
    level_dict = {'key': 'level'}

    # count elements each recipe
    for f in file_list:
        print(f)
        # --------------- #
        # define filepath #
        # --------------- #
        # ingredients path -> axis1
        ingredients_path = os.path.join(_INGREDIENTS_DIR, f)
        key_fname, _ = os.path.splitext(f)
        # sentences path -> axis2
        sentences_fname = key_fname + '_ner_result.txt'
        sentences_path = os.path.join(_SENTENCES_DIR, sentences_fname)
        # actions path -> axis3, 4, 5
        actions_category_path = os.path.join(
            _ACTIONS_CATEGORY_DIR, 'action_category.json'
        )
        # recipedb(recipename) path -> for recipe title
        recipedb_path = os.path.join(_RECIPEDB_DIR, f)

        # ------------------ #
        # fetch target value #
        # ------------------ #
        target_recipename = fetch_recipename(recipedb_path)
        count_ingredients = count_elements(ingredients_path)
        count_words = count_string_length(sentences_path)
        count_heat = count_action_category('加熱', sentences_path, actions_category_path)
        count_mix = count_action_category('混ぜる', sentences_path, actions_category_path)
        count_cut = count_action_category('切る', sentences_path, actions_category_path)

        title_dict.update({key_fname: target_recipename})
        axis1_dict.update({key_fname: count_ingredients})
        axis2_dict.update({key_fname: count_words})
        axis3_dict.update({key_fname: count_heat})
        axis4_dict.update({key_fname: count_mix})
        axis5_dict.update({key_fname: count_cut})

    # compute mean each axis values
    axis1_mean = compute_mean(axis1_dict)
    axis2_mean = compute_mean(axis2_dict)
    axis3_mean = compute_mean(axis3_dict)
    axis4_mean = compute_mean(axis4_dict)
    axis5_mean = compute_mean(axis5_dict)

    # add mean to each object dict
    title_dict.update({'mean': '平均'})
    axis1_dict.update({'mean': axis1_mean})
    axis2_dict.update({'mean': axis2_mean})
    axis3_dict.update({'mean': axis3_mean})
    axis4_dict.update({'mean': axis4_mean})
    axis5_dict.update({'mean': axis5_mean})

    # --------------------------- #
    # output data (original data) #
    # --------------------------- #
    output_data = output_jsondata(
        title_dict,
        axis1_dict,
        axis2_dict,
        axis3_dict,
        axis4_dict,
        axis5_dict
    )
    data = json.loads(output_data)
    dst_filepath = os.path.join(_OUTPUT_DIR, 'radar-chart-orgparams.json')
    with open(dst_filepath, 'w', encoding='utf-8') as w:
        json.dump(data, w, indent=4, ensure_ascii=False)
    print(output_data)

    # delete mean from original value
    del axis1_dict['mean']
    del axis2_dict['mean']
    del axis3_dict['mean']
    del axis4_dict['mean']
    del axis5_dict['mean']

    # compute max each axis
    axis1_score_max = compute_max(axis1_dict)
    axis2_score_max = compute_max(axis2_dict)
    axis3_score_max = compute_max(axis3_dict)
    axis4_score_max = compute_max(axis4_dict)
    axis5_score_max = compute_max(axis5_dict)

    # standardization dict value by level
    axis1_dict_std = standardization_by_level(axis1_dict, axis1_score_max, 5)
    axis2_dict_std = standardization_by_level(axis2_dict, axis2_score_max, 5)
    axis3_dict_std = standardization_by_level(axis3_dict, axis3_score_max, 5)
    axis4_dict_std = standardization_by_level(axis4_dict, axis4_score_max, 5)
    axis5_dict_std = standardization_by_level(axis5_dict, axis5_score_max, 5)

    # compute level each recipe
    for idx, (v1, v2, v3, v4, v5, k) in enumerate(zip(axis1_dict_std.values(),
                                                   axis2_dict_std.values(),
                                                   axis3_dict_std.values(),
                                                   axis4_dict_std.values(),
                                                   axis5_dict_std.values(),
                                                   title_dict.keys())):
        if k == 'key':
            pass
        else:
            all_value = [v1, v2, v3, v4, v5]
            target_value = max(all_value)
            level_dict.update({str(k): target_value})

    # compute mean each axis
    axis1_mean = compute_mean(axis1_dict_std)
    axis2_mean = compute_mean(axis2_dict_std)
    axis3_mean = compute_mean(axis3_dict_std)
    axis4_mean = compute_mean(axis4_dict_std)
    axis5_mean = compute_mean(axis5_dict_std)
    level_mean = compute_mean(level_dict)

    # add mean to each object dict
    axis1_dict_std.update({'mean': axis1_mean})
    axis2_dict_std.update({'mean': axis2_mean})
    axis3_dict_std.update({'mean': axis3_mean})
    axis4_dict_std.update({'mean': axis4_mean})
    axis5_dict_std.update({'mean': axis5_mean})
    level_dict.update({'mean': level_mean})


    # output data (standardization)
    output_data = output_jsondata(
        title_dict,
        axis1_dict_std,
        axis2_dict_std,
        axis3_dict_std,
        axis4_dict_std,
        axis5_dict_std,
        level_dict
    )
    data = json.loads(output_data)
    dst_filepath = os.path.join(_OUTPUT_DIR, 'radar-chart.json')
    with open(dst_filepath, 'w', encoding='utf-8') as w:
        json.dump(data, w, indent=4, ensure_ascii=False)

    print('********************************')
    print('level_dict')
    print(level_dict)
    print('********************************')


if __name__ == '__main__':
    main()
