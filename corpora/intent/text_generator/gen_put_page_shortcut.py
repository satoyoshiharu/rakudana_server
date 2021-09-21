import random

OBJECT = ['ページ','QRコード','QRコードのページ','インターネットのページ','ウェッブページ']
OBJ_MARKER = ['','を']
PLACE = ['スマホ','スマホ画面','ホーム画面']
PLACE_MARKER = ['','に','へ']
PUT_INTENT = ['置いて','置く','置け','貼り付けて','貼り付ける','貼り付け']
PLACE_MARKER2 = ['から','で']
PUT_INTENT2 = ['すぐ出せるようにして','出せるようにして',
               'すぐ出せるようにして','出せるようにして',
               'すぐ開けるようにして', '開けるようにして']
MOOD = ['','','','','','えーっと','んー','えー','あの']

if __name__ == "__main__":
    with open('../texts/put_page_shortcut.txt', 'w') as f:
        for i in range(500):
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}'+\
                f'{random.choice(PLACE)}{random.choice(PLACE_MARKER)}'+\
                f'{random.choice(PUT_INTENT)}\n')
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(PLACE)}{random.choice(PLACE_MARKER)}'+\
                f'{random.choice(PUT_INTENT)}\n')
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(PLACE)}{random.choice(PLACE_MARKER)}'+ \
                f'{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}' + \
                f'{random.choice(PUT_INTENT)}\n')
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}'+\
                f'{random.choice(PUT_INTENT)}\n')
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}'+ \
                f'{random.choice(PLACE)}{random.choice(PLACE_MARKER2)}' + \
                f'{random.choice(PUT_INTENT2)}\n')
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(PLACE)}{random.choice(PLACE_MARKER2)}' + \
                f'{random.choice(PUT_INTENT2)}\n')
            f.write(
                f'{random.choice(MOOD)}、'+\
                f'{random.choice(OBJECT)}{random.choice(OBJ_MARKER)}'+ \
                f'{random.choice(PUT_INTENT2)}\n')
