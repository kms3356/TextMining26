from keras.models import load_model
from konlpy.tag import Okt
import joblib
from keras.utils import pad_sequences
class SentimentAnalyzer:
    def __init__(self, model_file, encoder_file):
        self.model =  load_model(model_file)
        self.encoder = joblib.load(encoder_file)
        self.korean_tokenizer = Okt().morphs

    def sentiment_predict(self, text):
        tokens = [word for word in self.korean_tokenizer.morphs(text)]
        encoded_tokens = self.encoder.texts_to_sequence([tokens])
        X = pad_sequences(encoded_tokens, maxlen=self.model.input_shape[1]) # model에 input length 추가
        result = self.model.predict(X, verbose=0)
        labels=['부정', '긍정']
        result_index = np.argmax(results[0])
        output = labels[result_index]
        return output, result[0][result_index]