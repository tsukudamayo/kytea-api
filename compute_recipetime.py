import os
import json
from typing import List
from functools import reduce
from operator import add


def summation_time(wakati_array: List, time_params: dict) -> int:
    target = [time_params[n] for n in wakati_array if n in time_params]
    return reduce(add, target)


def extract_actionword(wakati_str: str) -> List:
    strings = wakati_str.split(' ')
    action_strings = [n for n in strings if n.find('Ac') >= 0]
    action_words = [n.split('/')[0] for n in action_strings]

    return action_words


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
