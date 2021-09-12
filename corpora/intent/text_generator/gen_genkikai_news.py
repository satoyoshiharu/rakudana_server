import random

GENKIKAI_INTENT = [
    '元気かいのお知らせ','NPO元気かい、お知らせ','元気かい、お知らせ',
    '元気かいのお知らせページを開いて','元気かいお知らせページ',
    '元気かいからのお知らせ','元気かいのお知らせを教えて',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/genkikai_news.txt', 'w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
