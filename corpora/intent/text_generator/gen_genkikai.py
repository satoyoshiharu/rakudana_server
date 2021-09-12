import random

GENKIKAI_INTENT = ['元気かい','NPO元気かい','元気かいの件','元気かいのこと']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/genkikai.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
