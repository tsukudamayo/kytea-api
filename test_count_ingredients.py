from count_ingredients import ingredient_list_to_dict


def test_ingredient_list_to_dict():
    with open('./test_data/copy_paste_sample.txt', 'r', encoding='utf-8') as r:
        test_data = r.read()
    expected = {
        '春菊': '1わ',
        '白すりごま': '大さじ3',
        'だし汁': '大さじ1',
        'しょうゆ': '大さじ1',
        '砂糖': '小さじ1',
        '塩': ''
    }
    result = ingredient_list_to_dict(test_data)

    assert result == expected
