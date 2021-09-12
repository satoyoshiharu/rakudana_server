if __name__ == '__main__':

  import sys
  import os
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  import config
  import com

  DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

  CORPORA_DIR = '../corpora/intent/text_generator/'
  CUR_DIR = os.getcwd()
  os.chdir(CORPORA_DIR)

  for i in range(1, com.INTENT_MAX+1): # 0 others text file is not generated
    print('gen_' + com.intents[i] + '.py...')
    exec(open('gen_' + com.intents[i] + '.py').read())

  os.chdir(CUR_DIR)

