import random
import random
GENKIKAI = ['元気かい','元気会','NPO元気かい','NPO元気会']
RECORD = ['履歴','履歴を']
KANRI_INTENT = [
    '管理する','管理','更新する','変更する','追加する','削除する',
    '更新', '変更', '追加', '削除',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/genkikai_manage_records.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(MOOD)}{random.choice(GENKIKAI)}の{random.choice(RECORD)}{random.choice(KANRI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(GENKIKAI)}{random.choice(RECORD)}{random.choice(KANRI_INTENT)}\n')
