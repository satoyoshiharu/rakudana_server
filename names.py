import pandas as pd

names = [
    ["A0001", "村田", "ムラタ", "慶子", "ケイコ", "Ufc60e681b482d59d3eeb1a24de4eec10"], #
    ["A0002", "佐藤", "サトウ", "良治", "ヨシハル", "U73303fce43ff02051ca356e36998145a"], #
    ["M0005", "浅井", "アサイ", "志津子", "シズコ", "U5fc4cf5108518959ab891766a1ad7d51"], #
    ["M0010", "東", "ヒガシ", "徳子", "トクコ", "U5d87647384a72f6800f82edd76efe3f6"], #
    ["M0012", "粟野", "アワノ", "勇", "イサム", "U3ebf3bb7d0ad8dac93c52bbddf8d0a3b"], #
    ["M0020", "伊東", "イトウ", "紀子", "ミチコ", "U2dd622df1ed1fcb3604809bac6aa78df"], #
    ["M0021", "伊藤", "イトウ", "京子", "キョウコ", "U6caaad394c742e3920cbe062e663fc85"], #きょうこ
    ["M0025", "今井", "イマイ", "利江", "トシエ", "U0c3499f0b6e1601f4abe3906a7ddcee3"], #あ
    ["M0031", "岩田", "イワタ", "恭子", "キョウコ", "Ua3f25b6862be7603f61a2323ca3183fc"],#
    ["M0034", "梅澤", "ウメザワ", "寿美子", "スミコ", "U2c86f92ce80acd2f2c4aa2b89bd8184e"],  #
    ["M0035", "越後谷", "エチゴヤ", "直史", "ナオフミ", "U564e6aecc510861a87a51703bc593fd5"], #
    ["M0040", "太田", "オオタ", "紋子", "アヤコ", "U984abcd76b1e5a6d69b342580c494331"],#
    ["M0044", "岡部", "オカベ", "恒子", "ツネコ", "U9fe8166bf5241670699d34974e8717d4"], #
    ["M0048", "小木曾", "オギソ", "加代子", "カヨコ", "U511bb1ebbf1b4118dab2876093226454"], #
    ["M0050", "奥田", "オクダ", "義信", "ヨシノブ", "U869a8cba9c3b0bd51afe8f7d16db1b0d"], #
    ["M0051", "奥村", "オクムラ", "幸枝", "サチエ", ""],
    ["M0053", "小栗", "オグリ", "典之", "ノリユキ", "U3b67b0080e87fe5c33e065bffeacea84"],
    ["M0056", "加賀", "カガ", "友子", "トモコ", ""],
    ["M0059", "加世田", "カセダ", "衣江", "キヌエ", ""],
    ["M0074", "倉田", "クラタ", "吉三", "トシゾウ", "Uc62e1e39e6be9b87a0c9325cf745dff4"], #
    ["M0090", "佐々木", "ササキ", "包美", "カネミ", "Ufa743dfcacb7c4771f1b8683152e12b8"], #
    ["M0097", "佐藤", "サトウ", "敏文", "トシフミ", "U324b060bb8a5e969f070d673318acc3f"], #
    ["M0098", "佐藤", "サトウ", "佳子", "ヨシコ", "Uf8048d6ab71d6c9dce9004b7852d4605"], #
    ["M0101", "蕃建", "シゲタテ", "千代", "チヨ", "U357c0c249d4f830d7fb14f071cf8e99b"], #
    ["M0102", "柴田", "シバタ", "ゆり", "ユリ", "U034b8490e86da6ad6d5f0648361416c5"], #
    ["M0103", "島田", "シマダ", "喜代子", "キヨコ","U9eaedcaf69309ebb504bcadc344fc910"], #
    ["M0107", "鈴木", "スズキ", "千恵子", "チエコ", ""],
    ["M0116", "高橋", "タカハシ", "富美子", "フミコ", "U3e440a818929ddfc73ce2b4e4bd52a71"], #
    ["M0122", "竹内", "タケウチ", "尚子", "ヒサコ", "U2c593b6cc84ec6114491576f287de8ea"], #
    ["U0016", "竹内", "タケノウチ", "美津恵", "ミツエ", ""],
    ["M0127", "田中", "タナカ", "知子", "トモコ", "U170872c3651af4b269a9a15c0f7a3e57"], #
    ["M0137", "所", "トコロ", "美栄子", "ミエコ", "U6b780e3bc04cb3fa7e868c73901d7531"], #Mie
    ["M0141", "中越", "ナカコシ", "洋子", "ヨウコ", "Ua93b46fa3939ef58c7786878f9b70abc"], #ひろこ？
    ["M0142", "中島", "ナカジマ", "孝子", "タカコ", "Ub8577613c5715cab7c5d333ee049403c"], #
    ["M0145", "中根", "ナカネ", "文子", "フミコ", "U1198d1b1b43ab86568507f7f92af5697"], #
    ["M0146", "中野", "ナカノ", "憶", "オク", "U0aecf893627fef22fe5b5f767ff7b7ae"], #
    ["M0148", "中原", "ナカハラ", "弘子", "ヒロコ", "U5419796713627b02d352bf8bac91a6d1"], #
    ["M0149", "中道", "ナカミチ", "淳司", "ジュンジ", "U8049b1b35e092c5987a835810491104e"], #
    ["M0156", "野村", "ノムラ", "建夫", "タテオ", "Ube9d61de9d8863c4ef27732533abcf1e"], #
    ["M0159", "長谷井", "ハセイ", "典子", "ノリコ", ""],
    ["M0166", "原", "ハラ", "満美子","マミコ","U0f472ee9f21d0fd1ff4e76414bc28168"], #
    ["M0168", "久留", "ヒサトメ", "正秀", "マサヒデ", "Ue25373ca7df45fd53d6cdbe1cc592953"], #
    ["M0185", "牧野", "マキノ", "久吉", "ヒサヨシ", "U831638f728e4f5a2f8fad156e6169d28"], #Q
    ["M0186", "正木", "マサキ", "直恵", "ナオエ", "Ub7a49a3330a6a579d2f64440a750a8c6"], #
    ["M0189", "馬渕", "マブチ", "寿美子", "スミコ", "U2840d5f963fae01cf822540658d79579"], #
    ["M0202", "森田", "モリタ", "隆人", "タカヒト", "Ub7dd70449265f10452d4fab56023d6dc"], #
    ["M0227", "渡辺", "ワタナベ", "美津子", "ミツコ", "U5151952f3b438d67833529df4d5dee24"], #
    ["M0232", "千草", "チグサ", "啓司", "ケイジ", "Ub54c08ff8e95010dead65cb494a35fd5"], #
    ["M0233", "加藤", "カトウ", "久美子", "クミコ", "Uaaa5f5b255030aab8a5812c1a594659b"], #
    ["M0235", "各務", "カガミ", "信夫", "ノブオ", "U47f1890747ff7c0dfd6b13238e0d98b1"], #
    ["M0236", "江口", "エグチ", "玉枝", "タマエ", "Ud1eda0d13daf6c016de30ca62099f9b8"], #
    ["M0237", "上馬場", "ウエババ", "孝子", "アツコ", "U472352c263639fd196b8a919850691ef"], #
    ["M0256", "朝比奈", "アサヒナ", "早紀子", "サキコ", "U48da2927859902bd909f62eb98f66a7b"],  #
    ["M0257", "相沢", "アイザワ", "京子", "キョウコ", "U252cb2c9daf9a75083ad39ad6958a780"], #
    ["M0262", "森川", "モリカワ", "晴子", "ハルコ", "U057667ff96e58a8cadffb6d8fa36d328"], #
    ["M0281", "木村", "キムラ", "稔", "ミノル", "Ue2f983f954d2e5e4c095948a6d79d19e"], #
    ["M0282", "伊藤", "イトウ", "時枝", "トキエ", "U3d9f221cbd2a5a2271d0275af78a7aee"], #サスケ
    ["M0283", "松本", "マツモト", "鈴子", "スズコ", "U7c17c4d9adb27aa5557823ac8618395f"],
    ["M0291", "高橋", "タカハシ", "美琴", "ミコト", "U6eeff5edb4c7cf7e04cb853bd8740762"],
]

nametable = pd.DataFrame(data=names, columns=["id", "sei", "seiyomi", "mei", "meiyomi", "lineid"])

