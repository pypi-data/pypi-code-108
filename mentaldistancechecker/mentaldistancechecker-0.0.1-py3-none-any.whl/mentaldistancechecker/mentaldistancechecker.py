import speech_recognition as sr
from transformers import pipeline 
from transformers import AutoModelForSequenceClassification 
from transformers import BertJapaneseTokenizer
import wave




def mentaldistancechecker(filepath, score=0):
    r = sr.Recognizer()

    with wave.open(filepath,  'rb') as wr:
        # 情報取得
        fr = wr.getframerate()#サンプリングレート
        fn = wr.getnframes()#フレームレート
        time = 1.0 * fn / fr#再生時間
    
    if time < 60:
        with sr.AudioFile(filepath) as source:#wavファイルを読み込み
            audio = r.record(source)


        kaiwatext = r.recognize_google(audio, language='ja-JP')#テキスト化し、変数に入れる
        #print(kaiwatext)

        #ネガポジ判定
        model = AutoModelForSequenceClassification.from_pretrained('daigo/bert-base-japanese-sentiment') 
        tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking') 
        nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer) 


        emo_text = nlp(kaiwatext)
        #print(emo_text)

        #ネガティブだったら-1して負の数に
        if emo_text[0]['label'] == 'ネガティブ':
            emo_score = emo_text[0]['score'] * -1
        else:
            emo_score = emo_text[0]['score']


        teigen =(time+1)/4
        men_score = 10 * emo_score * len(kaiwatext.replace(" ","")) * (1/teigen)
        score = score + men_score
        #print(score)
    
    
    print(f'友好スコアは：{score}です。')
    #友好スコアに応じて変化
    if score < 300:
        print(f'友達程度になるまでに必要なスコアは：{350 - score}です。')
    elif score < 340 :
        print(f'気の合う友人程度になるまでに必要なスコアは：{380 - score}です。')
    elif score < 400 :
        print(f'親友程度になるまでに必要なスコアは：{400 - score}です。')