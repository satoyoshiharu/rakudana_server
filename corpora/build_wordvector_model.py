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
#　Create tokens (word broken texts)
#
sp = spm.SentencePieceProcessor()
sp.Load("sentencepiece.model")
for src in glob.glob("./texts/*"):
    # 3. ファイルをひとつずつ処理していく。
    # src = "articles/AA/wiki_00"
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}:\t{src}')
    with codecs.open(src, 'r', 'utf-8') as f:
        sentences = []
        dst = DATA_FOLDER + f'/contents/wiki{len(glob.glob("./contents/wiki*"))+1}'
        lines = f.read().splitlines()
        for line in lines:
          words = " ".join(sp.EncodeAsPieces(line))
          sentences.append(words)
        print(*sentences, sep="\n", file=codecs.open(dst, 'w', 'utf-8'))
#
# Build Word Vector Model
#
SIZE = 100
MIN_COUNT = 300
WINDOW = 5
SG = 1
#dirname = f"size{SIZE}-min_count{MIN_COUNT}-window{WINDOW}-sg{SG}"
#if not DATA_FOLDER+"/model/"+dirname in glob.glob(DATA_FOLDER+"/model/*"):
#    os.mkdir(DATA_FOLDER+"/model/"+dirname)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = Word2Vec(
    PathLineSentences(DATA_FOLDER+'/contents'),
    vector_size=SIZE,
    min_count=MIN_COUNT,
    window=WINDOW,
    sg=SG,
    workers=4
)
model.save('wordvector.model')