import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))

OBJ = ['電卓','電卓','電卓','電卓','電卓','電卓アプリ','計算機']
CALCULATOR_INTENT = ['出して','出せ','使いたい','使う']
MOOD = ['えーと、','ちょっと、','すぐに']

if __name__ == "__main__":
    with open('../texts/calculator.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(OBJ)}\n')
            f.write(f'{random.choice(OBJ)}{random.choice(CALCULATOR_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(OBJ)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(OBJ)}{random.choice(CALCULATOR_INTENT)}\n')





