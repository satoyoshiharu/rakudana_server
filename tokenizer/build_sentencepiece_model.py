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

#DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'
DATA_FOLDER = '/media/sf_E_DRIVE/sentencepiece_data'
#iwanami, kenkyusha ej/je sentences, expressions + some wikipedia/texts
#
# Build sentencepiece model (aka word breaker)
#
def iter_files():
  #for textfile in glob.glob(DATA_FOLDER+"/texts/*"):
  for textfile in glob.glob(DATA_FOLDER+"/*.txt"):
    with codecs.open(textfile, 'r', 'utf-8') as f:
      lines = f.read().splitlines()
      for idx, line in enumerate(lines):
        #if idx%5==0 and len(line)>30: #todo: spm consume ram too much, so skip some
        yield line
spm.SentencePieceTrainer.Train(
    sentence_iterator=iter_files(),
    model_prefix='sentencepiece',
    character_coverage=0.9995,
    vocab_size=50000,
    model_type='unigram'
)

sp = spm.SentencePieceProcessor()
sp.Load("sentencepiece.model")
print(sp.EncodeAsPieces('今日は晴天です'))
print(sp.EncodeAsPieces('110番'))
print(sp.EncodeAsPieces('お父さんに電話'))
