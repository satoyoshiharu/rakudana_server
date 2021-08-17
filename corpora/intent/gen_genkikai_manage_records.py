import random

GENKIKAI_INTENT = [
    'げんきかいの記録を管理する','NPOげんきかい記録管理','げんきかいの記録を管理',
    'げんきかいの記録を更新する','げんきかいの記録を変更する','げんきかいの記録を追加する','げんきかいの記録を削除する',
    'げんきかいの記録更新', 'げんきかいの記録変更', 'げんきかいの記録追加', 'げんきかいの記録削除',
    'げんきかいの履歴を管理する', 'NPOげんきかい履歴管理', 'げんきかいの履歴を管理',
    'げんきかいの履歴を更新する', 'げんきかいの履歴を変更する', 'げんきかいの履歴を追加する', 'げんきかいの履歴を削除する',
    'げんきかいの履歴更新', 'げんきかいの履歴変更', 'げんきかいの履歴追加', 'げんきかいの履歴削除',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./genkikai_manage_records.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
