import random

SEI = ['佐藤','鈴木','高橋','田中','伊藤','渡辺','山本','中村','小林','加藤',
       '吉田','山田','佐々木','山口','松本','井上','木村','林','斉藤','清水',
       '山崎','森','池田','橋本','阿部','石川','山下','中島','石井','小川',
       '前田','岡田','長谷川','藤田','後藤','近藤','村上','遠藤','青木','坂本']
# https://www.meijiyasuda.co.jp/enjoy/ranking/year_men/boy.html
MEI_MALE = ['正一','清','辰雄','三郎','昭三','茂','勇','明','弘','勝',
            '稔','博','隆','誠','浩','健一','大輔','達也','翔太','拓也',
            '健太','大輝','翔','駿']
MEI_FEMALE = ['千代','正子','静子','文子','千代子','久子','幸子','和子','紀子','洋子',
              '恵子','久美子','由美子','明美','直美','陽子','智子','絵美','恵','裕子',
              '愛','美咲','明日香','萌']
SUFFIX = ['','さん','さん','さん','ちゃん']
CONTACT_MARKER = ['','','に','へ']
SEND_INTENT = ['','送る','','送信','送信する','する','して']
OBJ = ['メッセージ','メッセ','SMS','ショートメッセージ','SMSメッセージ']
OBJ_MARKER = ['','を']
MODE = ['','','','すぐに','いまから','ちょっと']

if __name__ == "__main__":
    with open('./send_short_message.txt','w') as f:
        for i in range(300):
            contactNames = [
                random.choice(SEI), random.choice(MEI_MALE), random.choice(MEI_FEMALE),
                random.choice(SEI) + random.choice(MEI_MALE), random.choice(SEI) + random.choice(MEI_FEMALE)
            ]
            contact = f'{random.choice(contactNames)}{random.choice(SUFFIX)}'
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