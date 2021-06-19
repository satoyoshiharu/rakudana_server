import random

YES_INTENT = ['はい','そう','ええ','うん','そうです','そうだ','はいよ','そうよ','イエス','OK','OKです']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./yes.txt','w') as f:
        for i in range(100):
            f.write(f'{random.choice(YES_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(YES_INTENT)}\n')
