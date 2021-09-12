import random

GENKIKAI_INTENT = ['元気かい管理','NPO元気かい管理','元気かいの管理']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/genkikai_admin.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
