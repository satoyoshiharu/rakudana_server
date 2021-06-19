import random

CANCEL_INTENT = ['キャンセル','取り消し','取り消す','取りやめ','やめる','やめ']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./cancel.txt','w') as f:
        for i in range(100):
            f.write(f'{random.choice(CANCEL_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(CANCEL_INTENT)}\n')
