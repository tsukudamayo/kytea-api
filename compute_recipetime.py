import os
import json
from typing import List
from functools import reduce
from operator import add
from collections import Counter


def summation_time(wakati_array: List, time_params: dict) -> int:
    target = [time_params[n] for n in wakati_array if n in time_params]

    return adjust_time_by_paramter(reduce(add, target, 0))
    # return reduce(add, time)


def adjust_time_by_paramter(time: int) -> int:

    if time > 5:
        return time
    else:
        return time + 5


def split_tag(tag_word):
    target_word = ''
    if tag_word == '/':
        target_word = '/'
    else:
        target_word = tag_word.split('/')[0]

    return target_word


def extract_actionword(ner_str: str) -> List:
    strings = ner_str.split(' ')
    action_strings = [n for n in strings if n.find('Ac') >= 0]
    action_words = [split_tag(n) for n in action_strings]

    return action_words


def count_actionword(ner_str: str, action_words: List) -> List:
    split_strings = ner_str.split(' ')
    delete_tag_array = [split_tag(n) for n in split_strings]
    action_collect = Counter(delete_tag_array)
    action_count_map = [{"action": k, "count": v} for k, v in action_collect.items() if k in action_words]

    return action_count_map


def debug_params(wakati_array: List, time_params: dict) -> dict:
    debug_log = {}
    for n in wakati_array:
        if n not in time_params:
            continue
        if n in debug_log:
            debug_log[n] += time_params[n]
        else:
            debug_log.update({n: time_params[n]})

    # debug_log = {n: time_params[n] for n in wakati_array if n in time_params}

    return debug_log


def fetch_timeparams(target_file: str) -> dict:
    with open(target_file, 'r', encoding='utf-8') as r:
        jsondata = json.load(r)

    return jsondata


def eval_time_strings(ner_str: str) -> List:
    time_strings = []
    split_strings = ner_str.split(' ')
    delete_tag_array = [n for n in split_strings]
    decimal_flg = False
    tmp_word = ''
    for w in delete_tag_array:
        if w.isdecimal() and decimal_flg is False:
            decimal_flg = True
            tmp_word += w
        elif w.isdecimal() and decimal_flg is True:
            tmp_word += w
        elif w.isdecimal() is False and decimal_flg is True:
            decimal_flg = False
            if w == '分':
                time_strings.append(int(tmp_word))
            tmp_word = ''
        else:
            pass

    if len(time_strings) == 0:
        sum_strings = 0
    else:
        sum_strings = sum(time_strings)

    return sum_strings
