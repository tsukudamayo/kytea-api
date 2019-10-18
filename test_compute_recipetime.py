from compute_recipetime import summation_time


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
