from flask import Flask, jsonify, request
from flask_cors import CORS

import json

import nerpreprocess as ner


_KBM_MODEL = 'kytea-win-0.4.2/model/jp-0.4.7-1.mod'
_KNM_MODEL = 'kytea-win-0.4.2/RecipeNE-sample/recipe416.knm'
_KYTEA_PATH = 'kytea-win-0.4.2/kytea.exe'


app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
app.config['JOSN_SORT_KEYS'] = False


@app.route('/', methods=['POST'])
def api():
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
    )
    result = finalize.result_output()


    return jsonify({'status': 'OK', 'data': result})


if __name__ == '__main__':
    app.run()
