from __future__ import unicode_literals
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

import config

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(config.LINE_CHANNEL_SECRET)

# do
# curl -v -X GET https://api.line.me/v2/bot/followers/ids -H 'Authorization: Bearer {UAVgoe7Aoq6woQWnEnI02MS7/hLmwM1X+9b4o8IyDlvCcrCeTWE7bRwlvOsy7jcWFmQQ+6PgGX+6rFPWfQ5Bd9kaphbL8e5LHgh6zZgNo+NvKt4PMtOWfqdsxNBvvBsKd8y97tJG0TkQT51hHbdo1wdB04t89/1O/w1cDnyilFU='
# copy the output & paster here
#"U3d9f221cbd2a5a2271d0275af78a7aee"
ids = ["U170872c3651af4b269a9a15c0f7a3e57","U8049b1b35e092c5987a835810491104e","U831638f728e4f5a2f8fad156e6169d28","U9fe8166bf5241670699d34974e8717d4","Ub54c08ff8e95010dead65cb494a35fd5","Ufa743dfcacb7c4771f1b8683152e12b8","Uc62e1e39e6be9b87a0c9325cf745dff4","U2840d5f963fae01cf822540658d79579","U3b67b0080e87fe5c33e065bffeacea84","U6b780e3bc04cb3fa7e868c73901d7531","Ube9d61de9d8863c4ef27732533abcf1e","U0aecf893627fef22fe5b5f767ff7b7ae","U984abcd76b1e5a6d69b342580c494331","Ua3f25b6862be7603f61a2323ca3183fc","U3d9f221cbd2a5a2271d0275af78a7aee","Ufc60e681b482d59d3eeb1a24de4eec10","Ub7a49a3330a6a579d2f64440a750a8c6","U252cb2c9daf9a75083ad39ad6958a780","Ub8577613c5715cab7c5d333ee049403c","U5fc4cf5108518959ab891766a1ad7d51","U357c0c249d4f830d7fb14f071cf8e99b","U0f472ee9f21d0fd1ff4e76414bc28168","Ud1eda0d13daf6c016de30ca62099f9b8","U034b8490e86da6ad6d5f0648361416c5","U2dd622df1ed1fcb3604809bac6aa78df","U511bb1ebbf1b4118dab2876093226454","U73303fce43ff02051ca356e36998145a","U1198d1b1b43ab86568507f7f92af5697","U472352c263639fd196b8a919850691ef","U47f1890747ff7c0dfd6b13238e0d98b1","U3ebf3bb7d0ad8dac93c52bbddf8d0a3b","U2c86f92ce80acd2f2c4aa2b89bd8184e","Uaaa5f5b255030aab8a5812c1a594659b","U869a8cba9c3b0bd51afe8f7d16db1b0d","Ub7dd70449265f10452d4fab56023d6dc","U9eaedcaf69309ebb504bcadc344fc910","Ue25373ca7df45fd53d6cdbe1cc592953","U6caaad394c742e3920cbe062e663fc85","U2c593b6cc84ec6114491576f287de8ea","Ua93b46fa3939ef58c7786878f9b70abc","U0c3499f0b6e1601f4abe3906a7ddcee3","U564e6aecc510861a87a51703bc593fd5","U7c17c4d9adb27aa5557823ac8618395f","U5d87647384a72f6800f82edd76efe3f6","Uf8048d6ab71d6c9dce9004b7852d4605","U5151952f3b438d67833529df4d5dee24","U5419796713627b02d352bf8bac91a6d1","U057667ff96e58a8cadffb6d8fa36d328","U3e440a818929ddfc73ce2b4e4bd52a71","U324b060bb8a5e969f070d673318acc3f"]
#ids = ["U170872c3651af4b269a9a15c0f7a3e57","U8049b1b35e092c5987a835810491104e","U831638f728e4f5a2f8fad156e6169d28","U9fe8166bf5241670699d34974e8717d4","Ub54c08ff8e95010dead65cb494a35fd5","Ufa743dfcacb7c4771f1b8683152e12b8","Uc62e1e39e6be9b87a0c9325cf745dff4","U2840d5f963fae01cf822540658d79579","U3b67b0080e87fe5c33e065bffeacea84","U6b780e3bc04cb3fa7e868c73901d7531","Ube9d61de9d8863c4ef27732533abcf1e","U0aecf893627fef22fe5b5f767ff7b7ae","U984abcd76b1e5a6d69b342580c494331","Ua3f25b6862be7603f61a2323ca3183fc","Ufc60e681b482d59d3eeb1a24de4eec10","Ub7a49a3330a6a579d2f64440a750a8c6","U252cb2c9daf9a75083ad39ad6958a780","Ub8577613c5715cab7c5d333ee049403c","U5fc4cf5108518959ab891766a1ad7d51","U357c0c249d4f830d7fb14f071cf8e99b","U0f472ee9f21d0fd1ff4e76414bc28168","Ud1eda0d13daf6c016de30ca62099f9b8","U034b8490e86da6ad6d5f0648361416c5","U2dd622df1ed1fcb3604809bac6aa78df","U511bb1ebbf1b4118dab2876093226454","U73303fce43ff02051ca356e36998145a","U1198d1b1b43ab86568507f7f92af5697","U472352c263639fd196b8a919850691ef","U47f1890747ff7c0dfd6b13238e0d98b1","U3ebf3bb7d0ad8dac93c52bbddf8d0a3b","U2c86f92ce80acd2f2c4aa2b89bd8184e","Uaaa5f5b255030aab8a5812c1a594659b","U869a8cba9c3b0bd51afe8f7d16db1b0d","Ub7dd70449265f10452d4fab56023d6dc","U9eaedcaf69309ebb504bcadc344fc910","Ue25373ca7df45fd53d6cdbe1cc592953","U6caaad394c742e3920cbe062e663fc85","U2c593b6cc84ec6114491576f287de8ea","Ua93b46fa3939ef58c7786878f9b70abc","U0c3499f0b6e1601f4abe3906a7ddcee3","U564e6aecc510861a87a51703bc593fd5","U7c17c4d9adb27aa5557823ac8618395f","U5d87647384a72f6800f82edd76efe3f6","Uf8048d6ab71d6c9dce9004b7852d4605","U5151952f3b438d67833529df4d5dee24","U5419796713627b02d352bf8bac91a6d1","U057667ff96e58a8cadffb6d8fa36d328","U3e440a818929ddfc73ce2b4e4bd52a71","U324b060bb8a5e969f070d673318acc3f"]
#ids = ["U170872c3651af4b269a9a15c0f7a3e57","U8049b1b35e092c5987a835810491104e","U831638f728e4f5a2f8fad156e6169d28","U9fe8166bf5241670699d34974e8717d4","Ub54c08ff8e95010dead65cb494a35fd5","Ufa743dfcacb7c4771f1b8683152e12b8","Uc62e1e39e6be9b87a0c9325cf745dff4","U2840d5f963fae01cf822540658d79579","U6b780e3bc04cb3fa7e868c73901d7531","Ube9d61de9d8863c4ef27732533abcf1e","U0aecf893627fef22fe5b5f767ff7b7ae","U984abcd76b1e5a6d69b342580c494331","Ua3f25b6862be7603f61a2323ca3183fc","Ufc60e681b482d59d3eeb1a24de4eec10","Ub7a49a3330a6a579d2f64440a750a8c6","U252cb2c9daf9a75083ad39ad6958a780","Ub8577613c5715cab7c5d333ee049403c","U5fc4cf5108518959ab891766a1ad7d51","U357c0c249d4f830d7fb14f071cf8e99b","U0f472ee9f21d0fd1ff4e76414bc28168","Ud1eda0d13daf6c016de30ca62099f9b8","U034b8490e86da6ad6d5f0648361416c5","U2dd622df1ed1fcb3604809bac6aa78df","U511bb1ebbf1b4118dab2876093226454","U73303fce43ff02051ca356e36998145a","U1198d1b1b43ab86568507f7f92af5697","U472352c263639fd196b8a919850691ef","U47f1890747ff7c0dfd6b13238e0d98b1","U3ebf3bb7d0ad8dac93c52bbddf8d0a3b","Uaaa5f5b255030aab8a5812c1a594659b","U869a8cba9c3b0bd51afe8f7d16db1b0d","Ub7dd70449265f10452d4fab56023d6dc","U9eaedcaf69309ebb504bcadc344fc910","Ue2f983f954d2e5e4c095948a6d79d19e","Ue25373ca7df45fd53d6cdbe1cc592953","U6caaad394c742e3920cbe062e663fc85","U2c593b6cc84ec6114491576f287de8ea","Ua93b46fa3939ef58c7786878f9b70abc","U0c3499f0b6e1601f4abe3906a7ddcee3","U564e6aecc510861a87a51703bc593fd5","U5d87647384a72f6800f82edd76efe3f6","Uf8048d6ab71d6c9dce9004b7852d4605","U5151952f3b438d67833529df4d5dee24","U5419796713627b02d352bf8bac91a6d1","U057667ff96e58a8cadffb6d8fa36d328","U3e440a818929ddfc73ce2b4e4bd52a71","U324b060bb8a5e969f070d673318acc3f"]
try:
    for id in ids:
        profile = line_bot_api.get_profile(f'{id}')
        print(profile.display_name, profile.user_id)
except Exception as e:
    print(f'exception {e}')

'''
TOMOKO TNK U170872c3651af4b269a9a15c0f7a3e57
中道 淳司 U8049b1b35e092c5987a835810491104e
Qちゃん U831638f728e4f5a2f8fad156e6169d28　???
岡部恒子 U9fe8166bf5241670699d34974e8717d4
千種 Ub54c08ff8e95010dead65cb494a35fd5
佐々木包美 Ufa743dfcacb7c4771f1b8683152e12b8
倉田吉三 Uc62e1e39e6be9b87a0c9325cf745dff4
馬渕寿美子 U2840d5f963fae01cf822540658d79579
のりゆき U3b67b0080e87fe5c33e065bffeacea84 
Mie U6b780e3bc04cb3fa7e868c73901d7531
のむら Ube9d61de9d8863c4ef27732533abcf1e
O.NAKANO U0aecf893627fef22fe5b5f767ff7b7ae
太田紋子 U984abcd76b1e5a6d69b342580c494331
岩田  恭子 Ua3f25b6862be7603f61a2323ca3183fc
ケイコムラタ Ufc60e681b482d59d3eeb1a24de4eec10
正木直恵 Ub7a49a3330a6a579d2f64440a750a8c6
kyoko.ai U252cb2c9daf9a75083ad39ad6958a780
中島孝子 Ub8577613c5715cab7c5d333ee049403c
淺井志津子🐩 U5fc4cf5108518959ab891766a1ad7d51
蕃建　千代 U357c0c249d4f830d7fb14f071cf8e99b
原満美子 U0f472ee9f21d0fd1ff4e76414bc28168
江口玉枝 Ud1eda0d13daf6c016de30ca62099f9b8
柴田　ゆり U034b8490e86da6ad6d5f0648361416c5
伊東紀子 U2dd622df1ed1fcb3604809bac6aa78df
小木曽加代子 U511bb1ebbf1b4118dab2876093226454
佐藤 良治 U73303fce43ff02051ca356e36998145a
中根文子 U1198d1b1b43ab86568507f7f92af5697
Atsuko.U U472352c263639fd196b8a919850691ef
各務信夫 U47f1890747ff7c0dfd6b13238e0d98b1
粟野I U3ebf3bb7d0ad8dac93c52bbddf8d0a3b
梅澤 U2c86f92ce80acd2f2c4aa2b89bd8184e 
くみこ Uaaa5f5b255030aab8a5812c1a594659b
奥田義信 U869a8cba9c3b0bd51afe8f7d16db1b0d
森田 Ub7dd70449265f10452d4fab56023d6dc
島田 喜代子 U9eaedcaf69309ebb504bcadc344fc910
木村稔 Ue2f983f954d2e5e4c095948a6d79d19e ---
マサヒデ Ue25373ca7df45fd53d6cdbe1cc592953
京子 U6caaad394c742e3920cbe062e663fc85
尚子 U2c593b6cc84ec6114491576f287de8ea
ひろこ Ua93b46fa3939ef58c7786878f9b70abc
あ U0c3499f0b6e1601f4abe3906a7ddcee3
越後谷直史 U564e6aecc510861a87a51703bc593fd5
松本鈴子 U7c17c4d9adb27aa5557823ac8618395f
東徳子 U5d87647384a72f6800f82edd76efe3f6
佐藤 佳子 Uf8048d6ab71d6c9dce9004b7852d4605
渡邊美津子 U5151952f3b438d67833529df4d5dee24
中原弘子 U5419796713627b02d352bf8bac91a6d1
森川  晴子 U057667ff96e58a8cadffb6d8fa36d328
高橋富美子 U3e440a818929ddfc73ce2b4e4bd52a71
佐藤敏文 U324b060bb8a5e969f070d673318acc3f

'''
