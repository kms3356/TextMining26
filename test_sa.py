from sentiment_analyzer import SentimentAnalyzer

vectorizer_file = 'model/sa_movie_vectorizer.pkl'
model_file = 'model/sa_movie_model.pkl'
sa = SentimentAnalyzer(vectorizer_file, model_file)
reviews = {
    '영화가 너무 재미있다',
    '이게 영화냐? 나도 만들겠다',
    '개노잼',
    '개꿀잼',
    '영화가 너무 재미있다',
    '진짜 드럽게 재미있네',
    '영화가 너무 재미없다'
}
for review in reviews:
    print(f'{review} -> {sa.analyze_sentiment(review)}')
