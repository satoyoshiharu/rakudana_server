import MeCab
tagger = MeCab.Tagger(r"-u ./user.dic -d /var/lib/mecab/dic/ipadic-utf8/")
print(f'tagger type: {type(tagger)}')
print(tagger.parse('私'))  # preload dictionary
print(tagger.parse('佐藤良治'))  # preload dictionary
print(tagger.parse('110番'))  # preload dictionary
print(tagger.parse('090-2935-5792'))  # preload dictionary
print(tagger.parse('鈴木さんに電話'))  # preload dictionary
print(tagger.parse('お父さんに電話'))  # preload dictionary