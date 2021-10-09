import random

GENKIKAI = ['元気かい','元気会','NPO元気かい','NPO元気会','元気かいの','元気会の']
MY = ['私の','俺の','','']
YOYAKU_INTENT = [
    '予約', '予約確認', '予約状況',
    '予約を確認','予約を教えて','予約状況を教えて',
    '予約はどうなっている？','予約はどうなっている？','予約入っている？'
]
MOOD = ['えーっと、','んー、','えー、','あの、','','','','','']

if __name__ == "__main__":
    with open('../texts/genkikai_myreservation.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(MOOD)}{random.choice(MY)}{random.choice(GENKIKAI)}{random.choice(YOYAKU_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(GENKIKAI)}{random.choice(MY)}{random.choice(YOYAKU_INTENT)}\n')
