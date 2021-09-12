import random

GENKIKAI_INTENT = [
    '元気かいの記録を管理する','NPO元気かい記録管理','元気かいの記録を管理',
    '元気かいの記録を更新する','元気かいの記録を変更する','元気かいの記録を追加する','元気かいの記録を削除する',
    '元気かいの記録更新', '元気かいの記録変更', '元気かいの記録追加', '元気かいの記録削除',
    '元気かいの履歴を管理する', 'NPO元気かい履歴管理', '元気かいの履歴を管理',
    '元気かいの履歴を更新する', '元気かいの履歴を変更する', '元気かいの履歴を追加する', '元気かいの履歴を削除する',
    '元気かいの履歴更新', '元気かいの履歴変更', '元気かいの履歴追加', '元気かいの履歴削除',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/genkikai_manage_records.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
