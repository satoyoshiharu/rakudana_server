import os
import subprocess
import shlex
import glob
import config

UPDATE_INTENT_TEXTS = False
BUILD_TOKENIZER = False
UPDATE_WORDBREAK_DATA = False
BUILD_WORDVECTOR = False
UPDATE_INTENT_DATA = True
BUILD_INTENT_CLASSIFIER = True

DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'
INTENT_DATA_FOLDER = '/home/ysato/PycharmProjects/rakudana/corpora/intent'
CUR_DIR = os.getcwd() # intent_classifier

if UPDATE_INTENT_TEXTS:
    print('### create intent texts...')
    exec(open('./create_training_texts.py').read())

if BUILD_TOKENIZER:
    print('### build tokenizer...')
    SP_DATA_FOLDER = '/media/sf_E_DRIVE/sentencepiece_data'
    for src in glob.glob(INTENT_DATA_FOLDER + "/*.txt"):
        subprocess.check_call(shlex.split(f'cp -f {src} {SP_DATA_FOLDER}'))
    os.chdir('../tokenizer')
    exec(open('./build_sentencepiece_model.py').read())

if UPDATE_WORDBREAK_DATA:
    os.chdir('../wordvector')
    WIKI_DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'
    print('### create tokenized text data...')
    for src in glob.glob(INTENT_DATA_FOLDER + "/*.txt"):
        subprocess.check_call(shlex.split(f'cp -f {src} {WIKI_DATA_FOLDER}/texts'))
    for src in glob.glob(WIKI_DATA_FOLDER + "/wordbreaks/*"):
        subprocess.check_call(shlex.split(f'rm -f {src}'))
    exec(open('./create_wb_files.py').read())

if BUILD_WORDVECTOR:
    os.chdir('../wordvector')
    print('### build word vector...')
    exec(open('./build_wordvector_model.py').read())

if UPDATE_INTENT_DATA:
    os.chdir(CUR_DIR)
    print('### create intent classifier binary data...')
    exec(open('./create_training_data.py').read())

if BUILD_INTENT_CLASSIFIER:
    print('### build intent_classifier...')
    os.chdir(CUR_DIR)
    exec(open('./train.py').read())
    exec(open('./test.py').read())