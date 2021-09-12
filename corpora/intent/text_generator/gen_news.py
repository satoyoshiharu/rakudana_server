import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))

NEWS_OBJ = ['ニュース','ニュースアプリ','ニュース記事']
NEWS_INTENT = ['を出して','出して','を読みたい','読みたい','開いて','を開いて']
MOOD = ['','','','えーと、','ちょっと、']

if __name__ == "__main__":
    with open('../texts/news.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(MOOD)}{random.choice(NEWS_OBJ)}{random.choice(NEWS_INTENT)}\n')





