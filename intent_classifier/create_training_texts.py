if __name__ == '__main__':

  import sys
  import os
  sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  import config
  import com

  DATA_FOLDER = '/media/sf_E_DRIVE/wikipedia'

  CORPORA_DIR = '../corpora/intent/'
  CUR_DIR = os.getcwd()
  os.chdir(CORPORA_DIR)

  for i in range(1, len(com.intents)): # 0 others text file is not generated
    print('gen_' + com.intents[i] + '.py...')
    exec(open('gen_' + com.intents[i] + '.py').read())

  # exec(open('gen_help.py').read())
  # exec(open('gen_yes.py').read())
  # exec(open('gen_no.py').read())
  # exec(open('gen_cancel.py').read())
  # exec(open('gen_retry.py').read())
  # exec(open('gen_tel.py').read())
  # exec(open('gen_call_police.py').read())
  # exec(open('gen_call_emergency.py').read())
  # exec(open('gen_send_line_message.py').read())
  # exec(open('gen_send_short_message.py').read())
  # exec(open('gen_genkikai.py').read())
  # exec(open('gen_genkikai_admin.py').read())
  # exec(open('gen_genkikai_myreservation.py').read())
  # exec(open('gen_genkikai_news.py').read())
  # exec(open('gen_genkikai_manage_records.py').read())
  # exec(open('gen_genkikai_manage_reservations.py').read())

  os.chdir(CUR_DIR)

