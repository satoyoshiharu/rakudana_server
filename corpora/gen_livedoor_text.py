import codecs
import glob
from bs4 import BeautifulSoup
from datetime import datetime
import sentencepiece as spm
import logging
from gensim.models.word2vec import Word2Vec, PathLineSentences
import os

DATA_FOLDER = '/media/sf_E_DRIVE/ldcc-20140209'

#
# Create plain texts
#
dirlist = glob.glob(DATA_FOLDER+"/text/*")
for dirname in dirlist:
    dst = dirname+'.txt'
    sentences = []
    for src in glob.glob(dirname+"/*.txt"):
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}:\t{src}')
        with codecs.open(src, 'r', 'utf-8') as f:
            lines = f.read().replace('。', '。\n').splitlines()
            for line in lines:
                if line.isalnum() or line.isascii(): continue
                if len(line)<10: continue
                sentences.append(line)
    print(*sentences, sep="\n", file=codecs.open(dst, 'w', 'utf-8'))