import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent'))
import personalname as pn

TEL_INTENT = ['電話','電話','電話','電話する','電話をかける','電話したい','電話かける']
OBJ_MARKER = ['','','に','へ','と']
MODE = ['','','','すぐに','いまから','ちょっと']

if __name__ == "__main__":
    with open('./tel.txt','w') as f:
        for i in range(500):
            contactNames = [
                random.choice(pn.SEI), random.choice(pn.MEI_MALE), random.choice(pn.MEI_FEMALE),
                random.choice(pn.SEI) + random.choice(pn.MEI_MALE), random.choice(pn.SEI) + random.choice(pn.MEI_FEMALE),
                random.choice(pn.FAMILY), random.choice(pn.SENIOR_SERVICES)
            ]
            contact = f'{random.choice(contactNames)}{random.choice(pn.SUFFIX)}{random.choice(OBJ_MARKER)}'
            mood = f'{random.choice(MODE)}'
            number = random.choice(
                [str(random.randrange(1000)) + str(random.randrange(1000)) + str(random.randrange(1000)),
                 str(random.randrange(1000)) + '-' + str(random.randrange(1000)) + '-' + str(random.randrange(1000)),
                 ])
            f.write(f'{mood}{random.choice(TEL_INTENT)}\n')
            f.write(f'{mood}{contact}{random.choice(TEL_INTENT)}\n')
            f.write(f'{mood}{number}に{random.choice(TEL_INTENT)}\n')
            f.write(f'{mood}{random.choice(TEL_INTENT)}、{contact}\n')
            f.write(f'{contact}{mood}{random.choice(TEL_INTENT)}\n')
            f.write(f'{number}{mood}{random.choice(TEL_INTENT)}\n')
            f.write(f'{random.choice(TEL_INTENT)}、{mood}、{contact}\n')
            f.write(f'{random.choice(TEL_INTENT)}、{mood}、{number}\n')






