import random

GENKIKAI_INTENT = [
    'げんきかいのお知らせ','NPOげんきかい、お知らせ','げんきかい、お知らせ',
    'げんきかいのお知らせページを開いて','げんきかいお知らせページ',
    'げんきかいからのお知らせ','げんきかいのお知らせを教えて',
]
MOOD = ['えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('./genkikai_news.txt','w') as f:
        for i in range(300):
            f.write(f'{random.choice(GENKIKAI_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}、{random.choice(GENKIKAI_INTENT)}\n')
