from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

import os
import json

import pandas as pd

import nerpreprocess as ner
import compute_recipetime as cr
import count_ingredients as ci
import kyteagraph as ky


if os.name == 'nt':
    _KBM_MODEL = 'kytea-win-0.4.2/model/jp-0.4.7-1.mod'
    _KNM_MODEL = 'kytea-win-0.4.2/RecipeNE-sample/recipe416.knm'
    _KYTEA_PATH = 'kytea-win-0.4.2/kytea.exe'
else:
    _KBM_MODEL = 'kytea-0.4.7/model/jp-0.4.7-1.mod'
    _KNM_MODEL = 'kytea-0.4.7/RecipeNE-sample/recipe416.knm'
    _KYTEA_PATH = 'kytea'

_TIME_PARAMS = './action_time/orangepage/action_time.json'
_ACTIONS_CATEGORY_DIR = './action_category/orangepage'
_REFERENCE_DIR = './num_of_params'


app = Flask(__name__, static_folder='./build/static', template_folder='./build')
auth = HTTPBasicAuth()
users = {
    'panasonic': 'panasonic'
}
CORS(app, resources={r'/*': {'origins': '*'}})
app.config['JSON_AS_ASII'] = False
app.config['JOSN_SORT_KEYS'] = False


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@app.route('/')
@auth.login_required
def hello():
    return render_template('index.html')
    # return 'hello'

@app.route('/ner', methods=['POST'])
def ner_by_kytea():
    data = request.get_data()
    data = data.decode('utf-8')
    data = json.loads(data)
    data = data['data']
    data = data.replace(' ', '')
    print(data)
    print(type(data))
    morphology = ner.parse_recipe(data, _KBM_MODEL, _KYTEA_PATH)
    wakati = ner.insert_space_between_words(morphology)
    score = ner.ner_tagger_1(wakati, _KNM_MODEL, _KYTEA_PATH)
    ner_result = ner.ner_tagger_2(score)
    finalize = ner.Finalizer(
        wakati,
        ner_result,
        data
    )
    result = finalize.result_output()
    print('morphology', morphology)
    print('wakati', wakati)
    print('score', score)
    print('ner_result', ner_result)
    print('data', data)
    print('result', result)

    return jsonify({
        'status': 'OK',
        'data': result,
        'wakati': wakati
    })


@app.route('/time', methods=['POST'])
def eval_recipe_time():
    data = request.get_data()
    data = data.decode('utf-8')
    data = json.loads(data)
    ner = data['data'][0]
    wakati = data['data'][1]
    print(ner)
    print(type(ner))
    print(wakati)
    print(type(wakati))
    action_words = cr.extract_actionword(ner)
    compute_string_time = cr.eval_time_strings(wakati)
    time_params = cr.fetch_timeparams(_TIME_PARAMS)
    print(action_words)
    print(cr.summation_time(action_words, time_params))
    print(cr.debug_params(action_words, time_params))
    count_action = cr.count_actionword(ner, action_words)
    action_time = cr.summation_time(action_words, time_params)
    expected_time = action_time + compute_string_time
    time_params_array = [{'action': k, 'time': v} for k, v in time_params.items()]

    return jsonify({
        'status': 'OK',
        'count': count_action,
        'time': expected_time,
        'recipetime': compute_string_time,
        'actiontime': action_time,
        'params': time_params_array,
    })


@app.route('/level', methods=['POST'])
def eval_recipe_level():
    title_dict = {'key': 'レシピ名'}
    axis1_dict = {'key': '食材'}
    axis2_dict = {'key': '文字数'}
    axis3_dict = {'key': '加熱'}
    axis4_dict = {'key': '混ぜる'}
    axis5_dict = {'key': '切る'}

    level_dict = {'key': 'レベル'}

    data = request.get_data()
    data = data.decode('utf-8')
    data = json.loads(data)
    ingredients = data['data'][0]
    print(ingredients)
    print(type(ingredients))

    wakati = data['data'][1]
    print('wakati')
    print(wakati)

    actions_category_path = os.path.join(
        _ACTIONS_CATEGORY_DIR, 'action_category.json'
    )
    reference_data_path = os.path.join(
        _REFERENCE_DIR, 'radar-chart-orgparams.json'
    )

    ingredients_dict = ci.ingredient_list_to_dict(ingredients)
    print('ingredients_dict : ', ingredients_dict)
    count_ingredients = ci.count_elements(ingredients_dict)
    print('count_ingredients : ', count_ingredients)
    count_words = ci.count_string_length(ingredients)
    print('count_words : ', count_words)
    count_heat = ci.count_action_category('加熱', wakati, actions_category_path)
    count_mix = ci.count_action_category('混ぜる', wakati, actions_category_path)
    count_cut = ci.count_action_category('切る', wakati, actions_category_path)
    print('count_heat :', count_heat)
    print('count_mix : ', count_mix)
    print('count_cut : ', count_cut)
    with open(reference_data_path, 'r', encoding='utf-8') as r:
        reference_data = json.load(r)

    print('data[1] : ', reference_data[1].values())
    axis1_score_max = ci.compute_max(reference_data[1])
    axis2_score_max = ci.compute_max(reference_data[2])
    axis3_score_max = ci.compute_max(reference_data[3])
    axis4_score_max = ci.compute_max(reference_data[4])
    axis5_score_max = ci.compute_max(reference_data[5])
    print('1', axis1_score_max)
    print('2', axis2_score_max)
    print('3', axis3_score_max)
    print('4', axis4_score_max)
    print('5', axis5_score_max)

    axis1_dict_std = float(count_ingredients / axis1_score_max) * 5.0
    axis2_dict_std = float(count_words / axis2_score_max) * 5.0
    axis3_dict_std = float(count_heat / axis3_score_max) * 5.0
    axis4_dict_std = float(count_mix / axis4_score_max) * 5.0
    axis5_dict_std = float(count_cut / axis5_score_max) * 5.0
    level_dict_std = max([axis1_dict_std, axis2_dict_std, axis3_dict_std,
                          axis4_dict_std, axis5_dict_std])

    print('1', axis1_dict_std)
    print('2', axis2_dict_std)
    print('3', axis3_dict_std)
    print('4', axis4_dict_std)
    print('5', axis5_dict_std)
    print('level', level_dict_std)

    recipe_level = [
                    {"key": "食材", "name": "ingredients", "target": axis1_dict_std, "mean": 1.954192546583851 },
                    {"key": "文字数", "name": "senteces", "target": axis2_dict_std, "mean": 1.3047501045924113 },
                    {"key": "加熱", "name": "heat", "target": axis3_dict_std, "mean": 0.8819875776397513 },
                    {"key": "混ぜる", "name": "mix", "target": axis4_dict_std, "mean": 1.6247139588100672 },
                    {"key": "切る", "name": "cut", "target": axis5_dict_std, "mean": 1.2644188110026617 },
                    {"key": "レベル", "name": "level", "target": level_dict_std, "mean": 3 },
    ]

    return jsonify({
        'status': 'OK',
        'data': recipe_level,
    })


@app.route('/select', methods=['POST'])
def select_data():
    input_dir = './build/dest'
    if os.path.exists(input_dir) is False:
        os.makedirs(input_dir)
    data_list = os.listdir(input_dir)

    return jsonify({
        'status': 'OK',
        'data': data_list
    })


@app.route('/read', methods=['POST'])
def read_json():
    data = request.get_data()
    data = data.decode('utf-8')
    data = json.loads(data)
    data = data['data']
    print(data)
    print(type(data))

    input_dir = './build/dest'
    input_file = data['selectedData']
    print('input_file : ', input_file)
    input_path = os.path.join(input_dir, input_file)

    with open(input_path, 'r', encoding='utf-8') as r:
        data = json.load(r)
    print(data)
    print(type(data))

    return jsonify({
        'status': 'OK',
        'data': data,
    })


@app.route('/output', methods=['POST'])
def output_json():
    data = request.get_data()
    data = data.decode('utf-8')
    data = json.loads(data)
    data = data['data']
    print(data)
    print(type(data))

    from datetime import datetime
    now = datetime.now()

    output_dir = './build/dest'
    output_file = now.strftime('%Y%m%d-%H%M%S') + '.json'
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as w:
        json.dump(data, w, indent=4, ensure_ascii=False)

    return jsonify({'status': 'OK'})


@app.route('/flowgraph', methods=['POST'])
def flowgraph():
    data_dir = './graph_data'
    data = request.get_data()
    data = data.decode('utf-8')
    data = json.loads(data)
    data = data['data']
    print(data)
    print(type(data))

    # -----------------
    # output flowgraph
    # -----------------
    # likelifood data config
    index = [0, 2, 4, 5, 8]
    index_list = pd.DataFrame({
        'index': index,
    })
    likelihood_csv = os.path.join(data_dir, 'likelihood.csv')
    likelihood = ky.load_likelihood(likelihood_csv, index_list)

    rne_map = os.path.join(data_dir, 'rne_category.txt')

    print('**************** rne_to_num_map ****************')
    rne_to_num_map = ky.rne_to_num(rne_map)
    print(rne_to_num_map)

    print('**************** num_to_rne_map ****************')
    num_to_rne_map = ky.num_to_rne(rne_map)
    print(num_to_rne_map)

    print('**************** word_to_order ****************')
    word_order = ky.word_to_order(data)
    print(word_order)

    print('**************** word_rne_map ****************')
    word_to_rne_map = ky.word_to_rne(data)
    print('rne_word_map')
    print(word_to_rne_map)

    print('**************** rne_word_map ****************')
    rne_to_word_map = ky.rne_to_word(data)
    print('rne_word_map')
    print(rne_to_word_map)

    dependency_list = ky.parse_dependency(
        likelihood,
        word_order,
        word_to_rne_map,
        rne_to_num_map,
        num_to_rne_map,
        rne_to_word_map,
    )
    print('dependency_list')
    print(dependency_list)

    print('################ eval arcs ################')
    arc_tag_list = None
    word_to_id = os.path.join(data_dir, 'word_to_id.pkl')
    clf = os.path.join(data_dir, 'svc.pkl')
    matrix = os.path.join(data_dir, 'matrix.pkl')
    prediction_map = os.path.join(data_dir, 'prediction_map.pkl')

    arc_tag_list = ky.evaluate_arcs(
        dependency_list,
        word_to_id,
        clf,
        matrix,
        prediction_map,
    )

    print('dependency list')
    print(dependency_list)

    print('arc_tag_list')
    print(arc_tag_list)

    print('word_order')
    print(word_order)
    nodes = ['{ id: "' + str(w[0]) + '-' + str(w[1]) + '"}' for w in word_order]
    print('nodes')
    print(nodes)


    links = ['{ source: "' + str(w[0]) + '", target: "' + str(w[1]) + '"}' for w in dependency_list]
    print('links')
    print(links)

    return jsonify({
        'status': 'OK',
        'dependency': dependency_list,
        'arc': list(arc_tag_list)
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
