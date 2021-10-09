import random
GENKIKAI = ['元気かい','元気会','NPO元気かい','NPO元気会']
YOYAKU = ['予約','予約を','予約状況を']
KANRI_INTENT = [
    '管理する','管理','更新する','変更する','追加する','削除する',
    '更新', '変更', '追加', '削除',
]
MOOD = ['えーっと、','んー、','えー、','あの、','','','','','']

if __name__ == "__main__":
    with open('../texts/genkikai_manage_reservations.txt', 'w') as f:
        for i in range(1000):
            f.write(f'{random.choice(MOOD)}{random.choice(GENKIKAI)}の{random.choice(YOYAKU)}{random.choice(KANRI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(GENKIKAI)}{random.choice(YOYAKU)}{random.choice(KANRI_INTENT)}\n')
