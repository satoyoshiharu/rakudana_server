import glob
import re
import codecs

FOLDER = '/media/sf_E_DRIVE/岩波'
outf = open('./samples.txt','w')
with open(FOLDER+'/iwanami.txt','w') as outf:
    for src in glob.glob(FOLDER+"/*.utf8"):
        with open(src, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                line = re.sub(r'△','',line)

                head = re.findall(r'■０００３【([^】]+)',line)
                if len(head)==0: head = re.findall(r'■００１４【([^】]+)', line)
                if len(head)==0: head = re.findall(r'■０００２([あ-んア-ン]+)', line)
                if len(head) > 0:
                    head = head[0].replace('（','').replace('）','').replace('×','').replace('〈','').replace('〉','')
                    head = re.sub(r'[■０-９]*','',head)
                    #print(head)
                    outf.write(head+'\n')

                line = re.sub(r'（■００１３[あ-ん■０-９]+■００１４）','',line) #ルビ削除
                defs = re.findall(r'■００２[２４]([^■]+)',line)
                for d in defs:
                    if d[0]=='↓' or d[0]=='《': continue
                    d = re.sub(r'▽.*$','',d)
                    if len(head)>0:
                        d = re.sub(r'―',head,d)
                    if d[0]=='。':
                        d = d[1:]
                    if len(d)>0:
                        #print(d)
                        outf.write(d+'\n')
outf.close()