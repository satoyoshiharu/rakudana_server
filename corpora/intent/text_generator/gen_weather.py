import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))

WEATHER = ['天気','天気','天気','天気','天気予報','天気予報','気候','気温','湿度']
TIME = ['','','','','','今日の','今日の','今日の','明日の','明後日の']
WEATHER_INTENT = ['','','','は','教えて','を教えて','はどう？','どう','はどうか教えて','どうか教えて','どうなる','はどうなる']
MOOD = ['','','','えーと、','ちょっと、']

if __name__ == "__main__":
    with open('../texts/weather.txt', 'w') as f:
        for i in range(1000):
            f.write(f'{random.choice(MOOD)}{random.choice(TIME)}{random.choice(WEATHER)}{random.choice(WEATHER_INTENT)}\n')





