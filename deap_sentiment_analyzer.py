from keras.models import load_model
from konlpy.tag import Okt
import joblib
from keras.utils import pad_sequences
import numpy as np

class DeepSentimentAnalyzer:
    def __init__(self, model_file, encoder_file):
        self.model =  load_model(model_file)
        self.encoder = joblib.load(encoder_file)
        self.maxlen = 42
        self.stopwords = set([
    '의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', 
    '자', '에', '와', '한', '하다', '네', '음', '앗', '어', '것', '수', '그', '때', '다'
])
    def tokenize_and_remove_stopwords(self,text):
    # 혹시 모를 결측치(NaN/None) 에러 방지용 안전장치
        if not isinstance(text, str):
            return []
        
        # 1단계: 형태소 분석 및 어간 추출 (예: '재밌네요' -> '재밌다')
        tokens = Okt().morphs(text, stem=True)
        
        # 2단계: 뽑아낸 토큰 중 불용어 리스트에 없는 단어만 남기기
        clean_tokens = [word for word in tokens if word not in self.stopwords]
        
        return clean_tokens
    
    def sentiment_predict(self, text):
        tokens = [word for word in self.tokenize_and_remove_stopwords(text)]
        encoded_tokens = self.encoder.texts_to_sequence([tokens])
        X = pad_sequences(encoded_tokens, maxlen=self.maxlen) # model에 input length 추가
        result = self.model.predict(X, verbose=0)
        labels=['부정', '긍정']
        result_index = np.argmax(result[0])
        output = labels[result_index]
        return output, result[0][result_index]