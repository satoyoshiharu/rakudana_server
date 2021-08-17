import random

GENKIKAI_INTENT = [
    'げんきかいの予約','NPOげんきかい予約','げんきかいの予約を確認','げんきかいの予約状況',
    'げんきかいの予約を教えて','げんきかいの予約を確認','げんきかいの予約状況を教えて',
    'げんきかいの予約はどうなっている？','げんきかいの私の予約はどうなっている？','げんきかいの予約入っている？'
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./genkikai_myreservation.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
