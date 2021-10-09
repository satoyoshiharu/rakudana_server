import random

GENKIKAI = ['元気かい','元気会','NPO元気かい','NPO元気会']
GENKIKAI_INTENT = [
    'お知らせ','お知らせ',
    'のお知らせ', 'のお知らせ',
    'お知らせページを開いて','お知らせページ',
    'のお知らせページを開いて', 'のお知らせページ',
    'からのお知らせ','からのお知らせを教えて',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/genkikai_news.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
