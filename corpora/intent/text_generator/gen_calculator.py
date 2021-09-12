import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))

OBJ = ['電卓','電卓','電卓','電卓','電卓','電卓アプリ','計算機']
CALCULATOR_INTENT = ['','','','出して']
MOOD = ['','','','えーと','ちょっと']

if __name__ == "__main__":
    with open('../texts/calculator.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(MOOD)}{random.choice(OBJ)}{random.choice(CALCULATOR_INTENT)}\n')





