import random

RETRY_INTENT = ['やり直す','やり直し','もう一回','もういっぺん']
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./retry.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(RETRY_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(RETRY_INTENT)}\n')
