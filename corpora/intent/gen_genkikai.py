import random

GENKIKAI_INTENT = ['げんきかい','NPOげんきかい','げんきかいの件','げんきかいのこと']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./genkikai.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
