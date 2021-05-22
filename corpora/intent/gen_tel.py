import name
import random

TEL_INTENT = ['電話','電話','電話','電話する','電話をかける','電話したい','電話かける']
OBJ_MARKER = ['','','に','へ','と']
MODE = ['','','','すぐに','いまから','ちょっと']


if __name__ == "__main__":
    with open('../data/tel.txt','w') as f:
        for i in range(100):
            f.write(f'{random.choice(MODE)}{random.choice(TEL_INTENT)}\n')
            f.write(f'[人名]{random.choice(OBJ_MARKER)}、{random.choice(MODE)}{random.choice(TEL_INTENT)}\n')
            f.write(f'{random.choice(MODE)}{random.choice(TEL_INTENT)}、[人名]{random.choice(OBJ_MARKER)}\n')






