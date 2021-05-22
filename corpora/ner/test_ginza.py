import spacy
from spacy import displacy
nlp = spacy.load('ja_ginza')
doc = nlp('今日、横須賀に行ってきた。町田の鈴木久美子に３時間３０分５０秒電話をかけた。明日は、富士山に登る。２５日の９時から鈴木くんの家へ行く。')
for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
