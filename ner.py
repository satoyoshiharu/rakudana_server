from datetime import datetime


class Entity():
    def __init__(self):
        pass

class Person(Entity):
    def __init__(self, sei='', seiyomi='', mei='', meiyomi='', id='', lineid=''):
        super().__init__()
        self.sei = sei
        self.seiyomi = seiyomi
        self.mei = mei
        self.meiyomi = meiyomi
        self.id = id
        self.lineid = lineid

class Day(Entity):
    def __init__(self,year=None,month=None,day=None,ampm=None,hour=None,minutes=None):
        super().__init__()
        today = datetime.today()
        if year!='':
            self.year = year
        else:
            self.year = today.year
        if month!='':
            self.month = month
        else:
            self.month = today.month
        self.day = day
        self.ampm = ampm
        self.hour = hour
        self.minutes = minutes


class Reservation(Entity):
    def __init__(self):
        super().__init__()
        self.date = None
        self.memberlist = []
        #self.member = Person('','','')


class Visit(Entity):
    def __init__(self):
        super().__init__()
        self.date = None
        self.memberlist = []


class Digits(Entity):
    def __init__(self):
        super().__init__()
        self.value = 0


class NER():

    def __init__(self):
        self.entitylist = []

    def find_entity(self, morphs):
        print('NER.find_entity > ...')
        maxI = len(morphs) - 1
        i = 0
        while True:
            if i > maxI: break
            if 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞固有名詞人名姓*':
                pn = Person()
                pn.sei = morphs[i]['base']
                if i<maxI and 'pos' in morphs[i+1].keys() and morphs[i+1]['pos'] == '名詞固有名詞人名名*':
                    pn.mei = morphs[i+1]['base']
                    i += 1
                print(f'NER.find_entity > Person {pn.sei}{pn.mei}')
                self.entitylist.append(pn)
            elif 'pos' in morphs[i].keys() and morphs[i]['pos'] == '名詞固有名詞人名名*':
                pn = Person()
                pn.mei = morphs[i]['base']
                print(f'NER.find_entity > Person {pn.mei}')
                self.entitylist.append(pn)
            i += 1
