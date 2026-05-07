import pandas as pd
from collections import Counter
from konlpy.tag import Okt
def get_word_counts(df, column_name):
    if column_name not in df.columns:
        return None
    
    all_text = " ".join(df[column_name])
    okt = Okt()
    mytags = set(['Noun', 'Verb', 'Adjective'])
    my_stopwords = set('없다 필요없다 하는 한다 의하여 하여 있다 하며 하여야'.split())
    words = [word for word, tag in okt.pos(all_text) if tag in mytags and word not in my_stopwords and len(word) > 1]
    
    counts = Counter(words)
    return counts