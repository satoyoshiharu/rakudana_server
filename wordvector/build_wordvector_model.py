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
    workers=4
)
model.save('wordvector.model')

