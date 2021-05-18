#
# Environment setup
#
# pip install wikiextractor
# python -m wikiextractor.WikiExtractor jawiki-latest-pages-articles.xml.bz2 -b 10M -o articles
# pip install bs4
# pip install lxml
# pip install gensim
# pip install tqdm
# pip install sentencepiece

import codecs
import glob
from bs4 import BeautifulSoup
from datetime import datetime
import sentencepiece as spm
import logging
from gensim.models.word2vec import Word2Vec, PathLineSentences
import os

DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

#
# Create plain texts
#
dirlist = glob.glob(DATA_FOLDER+"/articles/*")
for dirname in dirlist:
    for src in glob.glob(dirname+"/*"):
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}:\t{src}')
        with codecs.open(src, 'r', 'utf-8') as f:
            soup = BeautifulSoup(f.read(), "lxml")
            doc_tags = soup.find_all("doc")
            sentences = []
            dst = DATA_FOLDER + f'/texts/wiki{len(glob.glob("./texts/wiki*")) + 1}'
            for doc in doc_tags:
                if len(doc.text) > 1000000:
                    print(f'doc parse failed {doc.text.splitlines()[:3]}')
                    continue
                content = ''.join(doc.text.splitlines()[3:])
                content = content.replace('。', '。\n')
                sentences.append(content)
            print(*sentences, sep="\n", file=codecs.open(dst, 'w', 'utf-8'))
