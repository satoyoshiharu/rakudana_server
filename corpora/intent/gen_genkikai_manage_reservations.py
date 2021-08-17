import random

GENKIKAI_INTENT = [
    'げんきかいの予約を管理する','NPOげんきかい予約管理','げんきかいの予約を管理','げんきかいの予約状況を管理',
    'げんきかいの予約を更新する','げんきかいの予約を変更する','げんきかいの予約を追加する','げんきかいの予約を削除する',
    'げんきかいの予約更新', 'げんきかいの予約変更', 'げんきかいの予約追加', 'げんきかいの予約削除',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./genkikai_manage_reservations.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
