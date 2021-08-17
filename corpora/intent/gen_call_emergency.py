import random

OBJ = '119番'
TEL_INTENT = ['','する','して','に電話','に電話して','に電話かける','呼び出す','呼び出して']
OBJ2 = '救急車'
TEL_INTENT2 = ['','を呼ぶ','呼ぶ','呼びに電話']
MODE = ['','','','すぐに','いまから','ちょっと']

if __name__ == "__main__":
    with open('./call_emergency.txt','w') as f:
        for i in range(500):
            intent = random.choice([OBJ+random.choice(TEL_INTENT), OBJ2+random.choice(TEL_INTENT2)])
            mood = random.choice(MODE)
            f.write(f'{mood}{intent}\n')
            f.write(f'{intent}{mood}\n')






