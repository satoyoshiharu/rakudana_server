import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))

NEWS_OBJ = ['ニュース','ニュースアプリ','ニュース記事']
NEWS_INTENT = ['出す','出して','出せ','読みたい','開く','開け','開いて']
OBJ_MARKER = ['を']
MOOD = ['えーと、','ちょっと、']

if __name__ == "__main__":
    with open('../texts/news.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(NEWS_OBJ)}\n')
            f.write(f'{random.choice(NEWS_OBJ)}{random.choice(NEWS_INTENT)}\n')
            f.write(f'{random.choice(NEWS_OBJ)}{OBJ_MARKER}{random.choice(NEWS_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(NEWS_OBJ)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(NEWS_OBJ)}{random.choice(NEWS_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(NEWS_OBJ)}{OBJ_MARKER}{random.choice(NEWS_INTENT)}\n')





