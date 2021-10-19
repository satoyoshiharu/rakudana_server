import random
import os.path, sys
sys.path.append(os.path.join('/home/ysato/PycharmProjects/rakudana/corpora/intent/text_generator'))
import placename as pn

FACILITY = ['郵便局','ポスト','交番','区役所','市役所',
            'コンビニ','コンビニエンスストア','薬屋','ドラッグストア','スーパー','ホームセンター','ディスカウントセンター',
            'ローソン','セブンイレブン','ユニクロ','しまむら','マクドナルド','クリエイト','オーケー',
            'レストラン','ラーメン屋','寿司屋','蕎麦屋','うどん','和食','八百屋','魚屋','肉屋','花屋','青果店',
            'サイゼリア','マクドナルド','丸亀',
            'ガソリンスタンド','ガススタンド','駐車場','パーキング','ホテル','旅館','公園','駅','バス停']
QUALIFIER = ['近くの','このあたりの','この辺の','そばの','','','','','']
LOOKFOR_INTENT = ['はどこ','どこ','はどこにある','どこにある',
                  'を探して','探して','探す',
                  'を見つけて','見つけて','見つける',
                  'を調べて','調べる',
                  'の場所は','場所','の場所','の場所はどこ'
                  ]
OBJ = ['地図','マップ']
OPEN_INTENT = ['','開いて','を開いて']
ROUTE = ['経路','行き方','道順','ルート']
ROUTE_INTENT = ['は','を教えて','を示して']

MOOD = ['','','','えーと、','ちょっと、']

if __name__ == "__main__":
    with open('../texts/map.txt', 'w') as f:
        for i in range(1000):
            PLACE = random.choice([random.choice(pn.CITY),random.choice(pn.STATION)])
            f.write(f'{random.choice(MOOD)}{random.choice(OBJ)}{random.choice(OPEN_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(QUALIFIER)}{random.choice(FACILITY)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(QUALIFIER)}{random.choice(FACILITY)}{random.choice(LOOKFOR_INTENT)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(QUALIFIER)}{random.choice(PLACE)}\n')
            f.write(f'{random.choice(MOOD)}{random.choice(QUALIFIER)}{random.choice(PLACE)}{random.choice(LOOKFOR_INTENT)}\n')
            PLACE1 = random.choice([random.choice(pn.CITY),random.choice(pn.STATION)])
            PLACE2 = random.choice([random.choice(pn.CITY),random.choice(pn.STATION)])
            f.write(f'{random.choice(MOOD)}{PLACE1}から{PLACE2}まで{random.choice(ROUTE)}{random.choice(ROUTE_INTENT)}\n')
            PLACE1 = random.choice([random.choice(pn.CITY),random.choice(pn.STATION)])
            PLACE2 = random.choice([random.choice(pn.CITY),random.choice(pn.STATION)])
            f.write(f'{random.choice(MOOD)}{PLACE1}から{PLACE2}までの{random.choice(ROUTE)}{random.choice(ROUTE_INTENT)}\n')






