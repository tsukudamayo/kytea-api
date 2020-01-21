import os
import sys
import json

import numpy as np
import pandas as pd

import requests


_SRC_DIR = './import_data/betterhome/'


def eval_time(time_label, summation_time):
    if time_label == '15分以内':
        if 15 >= summation_time:
            return 1
        else:
            return 0
    elif time_label == '15～30分':
        if 15 < summation_time and summation_time <= 30:
            return 1
        else:
            return 0
    elif time_label == '30～60分':
        if 30 < summation_time and summation_time <= 60:
            return 1
        else:
            return 0
    elif time_label == '60分以上':
        if 60 < summation_time:
            return 1
        else:
            return 0
    else:
        print('something wrong...')
        sys.exit(1)


def main():
    count = 0
    max_len = 100

    title_array = np.full(max_len, 'a', dtype=object)
    time_label_array = np.full(max_len, 'a', dtype=object)
    eval_time_array = np.full(max_len, 0)
    result_array = np.full(max_len, 0)
    
    file_list = os.listdir(_SRC_DIR)
    for f in file_list:
        if count == max_len:
            break
        filepath = os.path.join(_SRC_DIR, f)
        with open(filepath, 'r', encoding='utf-8') as r:
            data = json.load(r)

        title = data['title']
        time_label = data['time']
        recipe = data['recipe']
        
        print('data : ', data)
        print('title : ', title)
        print('recipe : ', recipe)
        res = requests.post('http://192.168.1.137:5000/ner', data=json.dumps({'data': recipe}))
        morph = res.json()
        print('response : ', morph)
        ner = morph['data']
        wakati = morph['wakati']
        time_res = requests.post(
            'http://192.168.1.137:5000/time',
            data=json.dumps({'data': [ner, wakati]})
        )
        time_res = time_res.json()
        print('time response : ', time_res)
        action_time = time_res['actiontime']
        recipe_time = time_res['recipetime']
        print('time_label : ', time_label)
        print('infer_time : ', action_time + recipe_time)
        summation_time = action_time + recipe_time
        
        result = eval_time(time_label, summation_time)
        print('eval : ', result)

        title_array[count] = title
        time_label_array[count] = time_label
        eval_time_array[count] = summation_time
        result_array[count] = result

        print('title_array : ', title_array)
        print('time_label_array : ', time_label_array)
        print('eval_time_array : ', eval_time_array)
        print('result_array : ', result_array)
        
        count += 1

    df = pd.DataFrame({
        'title': title_array,
        'time_label': time_label_array,
        'eval_time': eval_time_array,
        'result:': result_array
    })
    print('df')
    print(df)
    df.to_csv('result.csv', encoding='utf-8')
        

if __name__ == '__main__':
    main()
