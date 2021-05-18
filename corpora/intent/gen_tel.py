import name
import random

TEL_INTENT = ['電話','電話','電話','電話する','電話をかける','電話したい']
OBJ_MARKER = ['、','に','へ']

if __name__ == "__main__":
    with open('../data/tel_intents.txt','w') as f:
        for i in range(100):
            f.write(f'\n{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(name.SEI)}{random.choice(OBJ_MARKER)}{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(name.SEI)}{random.choice(name.SUFFIX)}{random.choice(OBJ_MARKER)}{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(name.MEI_MALE)}{random.choice(OBJ_MARKER)}{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(name.MEI_MALE)}{random.choice(name.SUFFIX)}{random.choice(OBJ_MARKER)}{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(name.MEI_FEMALE)}{random.choice(OBJ_MARKER)}{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(name.MEI_FEMALE)}{random.choice(name.SUFFIX)}{random.choice(OBJ_MARKER)}{random.choice(TEL_INTENT)}')
            f.write(f'\n{random.choice(TEL_INTENT)}、{random.choice(name.SEI)}{random.choice(OBJ_MARKER)}')
            f.write(f'\n{random.choice(TEL_INTENT)}、{random.choice(name.SEI)}{random.choice(name.SUFFIX)}{random.choice(OBJ_MARKER)}')
            f.write(f'\n{random.choice(TEL_INTENT)}、{random.choice(name.MEI_MALE)}{random.choice(OBJ_MARKER)}')
            f.write(f'\n{random.choice(TEL_INTENT)}、{random.choice(name.MEI_MALE)}{random.choice(name.SUFFIX)}{random.choice(OBJ_MARKER)}')
            f.write(f'\n{random.choice(TEL_INTENT)}、{random.choice(name.MEI_FEMALE)}{random.choice(OBJ_MARKER)}')
            f.write(f'\n{random.choice(TEL_INTENT)}、{random.choice(name.MEI_FEMALE)}{random.choice(name.SUFFIX)}{random.choice(OBJ_MARKER)}')






