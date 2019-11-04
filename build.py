#!/usr/bin/env python3
import os
import shutil

for root, subdirs, files in os.walk('cry-sage'):
    if '__pycache__' in root:
        continue
    for subdir in subdirs:
        if subdir == '__pycache__':
            continue
        if not os.path.exists(f'{root}/{subdir}'.replace('cry-sage', 'cry')):
            os.mkdir(f'{root}/{subdir}'.replace('cry-sage', 'cry'))
    for file in files:
        filename, _, suffix = file.partition('.')
        if suffix == 'sage':
            os.system(f'sage -preparse {root}/{filename}.sage')
            os.rename(f'{root}/{filename}.sage.py', f'{root}/{filename}.py'.replace('cry-sage', 'cry'))
        else:
            shutil.copyfile(f'{root}/{file}', f'{root}/{file}'.replace('cry-sage', 'cry'))
