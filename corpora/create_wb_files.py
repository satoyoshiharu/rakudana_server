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

def strip_spacemark(inputtokenlist):
    #print(inputtokenlist)
    outtokenlist = []
    for t in inputtokenlist:
        t = t.replace('▁','')
        if t!='':
            outtokenlist.append(t)
    #print(outtokenlist)
    return outtokenlist

#
#　Create tokens (word broken texts)
#
sp = spm.SentencePieceProcessor()
sp.Load("./sentencepiece.model")
for src in glob.glob(DATA_FOLDER + "/texts/*"):
    # 3. ファイルをひとつずつ処理していく。
    # src = "articles/AA/wiki_00"
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}:\t{src}')
    with codecs.open(src, 'r', 'utf-8') as f:
        sentences = []
        numFile = len(glob.glob(DATA_FOLDER + "/wordbreaks/*"))
        dst = DATA_FOLDER + f'/contents/wb{numFile+1}'
        lines = f.read().splitlines()
        for line in lines:
            if len(line)>0:
                word_break = sp.EncodeAsPieces(line)
                word_break = strip_spacemark(word_break)
                words = " ".join(word_break)
                sentences.append(words)
        print(*sentences, sep="\n", file=codecs.open(dst, 'w', 'utf-8'))
