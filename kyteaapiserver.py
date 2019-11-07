from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

import os
import json

import nerpreprocess as ner
import compute_recipetime as cr
import count_ingredients as ci

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
    data = data['data']
    print(data)
    print(type(data))
    action_words = cr.extract_actionword(data)
    compute_string_time = cr.eval_time_strings(data)
    time_params = cr.fetch_timeparams(_TIME_PARAMS)
    print(action_words)
    print(cr.summation_time(action_words, time_params))
    print(cr.debug_params(action_words, time_params))
    count_action = cr.count_actionword(data, action_words)
    action_time = cr.summation_time(action_words, time_params)
    expected_time = action_time + compute_string_time
    time_params_array = [{'action': k, 'time': v} for k, v in time_params.items()]

    return jsonify({
        'status': 'OK',
        'count': count_action,
        'time': expected_time,
        'recipetime': compute_string_time,
        'actiontime': action_time,
        'params': time_params_array
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

    print('1', axis1_dict_std)
    print('2', axis2_dict_std)
    print('3', axis3_dict_std)
    print('4', axis4_dict_std)
    print('5', axis5_dict_std)

    recipe_level = [
                    {"key": "食材", "target": axis1_dict_std, "mean": 1.954192546583851 },
                    {"key": "文字数", "target": axis2_dict_std, "mean": 1.3047501045924113 },
                    {"key": "加熱", "target": axis3_dict_std, "mean": 0.8819875776397513 },
                    {"key": "混ぜる", "target": axis4_dict_std, "mean": 1.6247139588100672 },
                    {"key": "切る", "target": axis5_dict_std, "mean": 1.2644188110026617 }
    ]

    return jsonify({
        'status': 'OK',
        'data': recipe_level,
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
