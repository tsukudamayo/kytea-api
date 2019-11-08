from compute_recipetime import summation_time
from compute_recipetime import extract_actionword
from compute_recipetime import count_actionword
from compute_recipetime import eval_time_strings


def test_count_actionword():
    action_words = [
                    "からめ", "つけ", "入れ", "切",
                    "加え", "取り除", "回し入れ",
                    "戻し入れ", "混ぜ", "混ぜ合わせ",
                    "炒め", "焼", "熱"
    ]
    expected = [
                {"action": "取り除", "count": 2},
                {"action": "切", "count": 6},
                {"action": "つけ", "count": 1},
                {"action": "からめ", "count": 1},
                {"action": "加え", "count": 1},
                {"action": "混ぜ合わせ", "count": 1},
                {"action": "熱", "count": 1},
                {"action": "焼", "count": 1},
                {"action": "入れ", "count": 1},
                {"action": "炒め", "count": 1},
                {"action": "混ぜ", "count": 3},
                {"action": "回し入れ", "count": 1},
                {"action": "戻し入れ", "count": 1},
    ]
    test_data = './test_data/count_actionword_test_text.txt'
    test_strings = open(test_data, 'r', encoding='utf-8').read()
    result = count_actionword(test_strings, action_words)
    print('result', result)

    assert result == expected


def test_extract_actionword():
    test_data = './test_data/count_actionword_test_text.txt'
    expected = [
                '取り除', '切', '切', 'つけ', 'からめ', '切',
                '取り除', '切', '切', '切', '加え', '混ぜ合わせ',
                '熱', '並べ入れ', 'た', '焼', 'あけ', 'た', '入れ',
                '炒め', '混ぜ', '回し入れ', '混ぜ', '戻し入れ', '混ぜ'
    ]
    test_strings = open(test_data, 'r', encoding='utf-8').read()
    result = extract_actionword(test_strings)
    print('result', result)

    assert result == expected


def test_summation_time():
    test_data = ['a', 'b', 'c', 'd', 'e']
    test_dict = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5
    }
    result = summation_time(test_data, test_dict)
    expected = 15
    assert result == expected


def test_eval_time_strings():
    test_data = './test_data/detail_121930_recipe_time_test.txt'
    test_strings = open(test_data, 'r', encoding='utf-8').read()
    print('test_strings : ', test_strings)

    expected = 40
    result = eval_time_strings(test_strings)

    assert result == expected


def test_eval_time_strings_detail_115975():
    test_data = './test_data/detail_115975_recipe_time_test.txt'
    test_strings = open(test_data, 'r', encoding='utf-8').read()
    print('test_strings : ', test_strings)

    expected = 10
    result = eval_time_strings(test_strings)

    assert result == expected


def test_eval_time_strings_detail_135917():
    test_data = './test_data/detail_135917_recipe_time_test.txt'
    test_strings = open(test_data, 'r', encoding='utf-8').read()
    print('test_strings : ', test_strings)

    expected = 43
    result = eval_time_strings(test_strings)

    assert result == expected
