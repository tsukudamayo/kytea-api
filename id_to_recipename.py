import os
import json
import shutil


_SRC_DIR = './import_data/orangepage'
_DST_DIR = './dst'


def main():
    error_count = 0
    file_list = os.listdir(_SRC_DIR)
    pairent_dir = os.path.basename(_SRC_DIR)
    dst_path = os.path.join(_DST_DIR, pairent_dir)
    if os.path.isdir(dst_path) is True:
        pass
    else:
        os.makedirs(dst_path)
    for f in file_list:
        src_filepath = os.path.join(_SRC_DIR, f)
        if os.path.isdir(src_filepath) is True:
            continue
        with open(src_filepath, 'r', encoding='utf-8') as r:
            try:
                data = json.load(r)
            except json.JSONDecodeError:
                print('JSONDecodeError')
                error_count += 1
                pass
        print('data : ', data)
        copy_fname = data['title']
        print('copy_fname : ', copy_fname)
        dst_filepath = os.path.join(dst_path, data['title'] + '.json')
        shutil.copy2(src_filepath, dst_filepath)
    print('error_count : ', error_count)


if __name__ == '__main__':
    main()
