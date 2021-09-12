import random

OBJECT = ['紙のメモ','メモ','手書きメモ','このメモ']
SAVE_INTENT = ['保存して','記録して','写真で保存して']
OBJ_MARKER = ['を','']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/save_memo.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}({random.choice(SAVE_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}{random.choice(SAVE_INTENT)}\n')
