from konlpy.tag import Okt
import joblib


class SentimentAnalyzer:
    def __init__(self, vectorizer_file, model_file):
        self.__vectorizer = joblib.load(vectorizer_file)
        self.__sa_model = joblib.load(model_file)
        self.my_tags = set(['Noun', 'Verb', 'Adjective'])
        self.my_stopwords = set('하는 한다 의하여 하여 있다 하며 하여야'.split())

    def korean_tokenizer(self, text):
        return [word for word, tag in Okt().pos(text) if tag in self.my_tags and word not in self.my_stopwords]
    
    # 함수 코드
    def analyze_sentiment(self, review):
        token_review = ' '.join(self.korean_tokenizer(review))
        # 전처리 및 특징 벡터 추출
        review_fv = self.__vectorizer.transform([token_review])
        # print(review_fv)

        result = self.__sa_model.predict(review_fv)
        # print(result)

        show = '긍정' if result[0] >= 0.5 else '부정'
        return show