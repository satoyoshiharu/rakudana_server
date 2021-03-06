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
from gensim.models import KeyedVectors
import os
import config

DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'
#
# Build Word Vector Model
#
SIZE = config.WORD_VECTOR_SIZE
MIN_COUNT = 50
WINDOW = 5
SG = 1
#dirname = f"size{SIZE}-min_count{MIN_COUNT}-window{WINDOW}-sg{SG}"
#if not DATA_FOLDER+"/model/"+dirname in glob.glob(DATA_FOLDER+"/model/*"):
#    os.mkdir(DATA_FOLDER+"/model/"+dirname)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = Word2Vec(
    PathLineSentences(DATA_FOLDER+'/wordbreaks'),
    vector_size=SIZE,
    min_count=MIN_COUNT,
    window=WINDOW,
    sg=SG,
    workers=3
)
model.save('wordvector.model')
wv_model = Word2Vec.load('wordvector.model')
wv_model.wv.save('wv.model')
model = KeyedVectors.load('wv.model')

print('父->', model.most_similar(positive='父'))
print('ユニクロ->', model.most_similar(positive='ユニクロ'))
print('メンチカツ->', model.most_similar(positive='メンチカツ'))
print('人vs父:', model.similarity('人','父'))
print('物vs父:', model.similarity('物','父'))
print('メンチカツvs料理', model.similarity('メンチカツ','料理'))
print('ラーメンvsレストラン', model.similarity('ラーメン','レストラン'))

