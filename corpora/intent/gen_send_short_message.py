import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent'))
import personalname as pn

CONTACT_MARKER = ['','','に','へ']
SEND_INTENT = ['','送る','','送信','送信する','する','して']
OBJ = ['メッセージ','メッセ','SMS','ショートメッセージ','SMSメッセージ']
OBJ_MARKER = ['','を']
MODE = ['','','','すぐに','いまから','ちょっと']

if __name__ == "__main__":
    with open('./send_short_message.txt','w') as f:
        for i in range(500):
            contactNames = [
                random.choice(pn.SEI), random.choice(pn.MEI_MALE), random.choice(pn.MEI_FEMALE),
                random.choice(pn.SEI) + random.choice(pn.MEI_MALE), random.choice(pn.SEI) + random.choice(pn.MEI_FEMALE),
                random.choice(pn.FAMILY), random.choice(pn.SENIOR_SERVICES)
            ]
            contact = f'{random.choice(contactNames)}{random.choice(pn.SUFFIX)}'
            obj = f'{random.choice(OBJ)}{random.choice(OBJ_MARKER)}'
            mood = f'{random.choice(MODE)}'
            f.write(f'{mood}{obj}{random.choice(SEND_INTENT)}\n')
            f.write(f'{mood}{contact}{obj}{random.choice(SEND_INTENT)}\n')
            f.write(f'{mood}{obj}{random.choice(SEND_INTENT)}\n')
            f.write(f'{contact}{mood}{obj}{random.choice(SEND_INTENT)}\n')
            f.write(f'{obj}{mood}{contact}{random.choice(SEND_INTENT)}\n')
            f.write(f'{obj}{mood}{contact}{random.choice(SEND_INTENT)}\n')
            f.write(f'{contact}{obj}{mood}{random.choice(SEND_INTENT)}\n')
            f.write(f'{obj}{contact}{mood}{random.choice(SEND_INTENT)}\n')
            f.write(f'{obj}{contact}{mood}{random.choice(SEND_INTENT)}\n')
