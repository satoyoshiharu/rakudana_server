import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))

WEATHER = ['天気','天気','天気','天気','天気予報','天気予報','気候','気温','湿度']
TIME = ['','','','','','今日','今日','今日','今日','明日','明後日']
WEATHER_INTENT = ['','','','は',
                  '教えて','を教えて','を調べて','を調べる'
                  'はどう','どう','はどうか教えて','どうか教えて','どうなる','はどうなる',
                  ]
MOOD = ['','','','えーと、','ちょっと、']
QUESTION = ['雨','晴れ','暑い','寒い','冷える']

if __name__ == "__main__":
    with open('../texts/weather.txt', 'w') as f:
        for i in range(500):
            f.write(f'{random.choice(MOOD)}{random.choice(WEATHER)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(TIME)}の{random.choice(WEATHER)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(TIME)}の{random.choice(WEATHER)}{random.choice(WEATHER_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(TIME)}は{random.choice(QUESTION)}かな\n')





