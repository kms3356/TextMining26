import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager, rc


def create_bar_chart(word_counts, top_n):
    font_path = "c:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)

    common_words = word_counts.most_common(top_n)
    words = [x for x,y in common_words][::-1]
    counts = [y for x,y in common_words][::-1]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(words, counts)
    ax.set_title(f"상위 {top_n}개 단어 빈도수")
    ax.set_xlabel("빈도수")
    ax.set_ylabel("단어")
    return fig

def create_wordcloud(word_counts, max_words):
    font_path="c:/Windows/Fonts/malgun.ttf"
    
    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        max_words=max_words,
        width=800,
        height=400
    )
    
    cloud = wc.generate_from_frequencies(word_counts)
    # figure 객체 만들고 워드클라우드 그리기
    fig = plt.figure(figsize=(12, 6))
    plt.imshow(cloud)
    plt.axis('off')
    return fig