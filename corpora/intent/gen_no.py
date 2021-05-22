import name
import random

YES_INTENT = ['いえ','いいえ','いや','違う','違います','違うよ','ノー','そうじゃない','そうじゃなくって']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../data/no.txt','w') as f:
        for i in range(100):
            f.write(f'{random.choice(YES_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(YES_INTENT)}\n')
