import streamlit as st
import pandas as pd
from mylib import myTextAnalyzer as ta
from mylib import myStreamlitVisualizer as vis

st.set_page_config(page_title="단어 빈도수 시각화", layout="wide")

# 사이드바 구성
with st.sidebar:
    st.header("파일 선택")
    uploaded_file = st.file_uploader("파일 업로드", type=['csv'])
    column_name = st.text_input("데이터가 있는 컬럼명", value="review")
    
    check_btn = st.button("데이터 파일 확인")
    
    st.divider()
    st.header("설정")
    
    show_bar = st.checkbox("빈도수 그래프", value=True)
    bar_n = st.slider("단어 수 (막대)", 10, 50, 20)
    
    show_wc = st.checkbox("워드클라우드")
    wc_n = st.slider("단어 수 (클라우드)", 20, 100, 50)
    
    start_btn = st.button("분석 시작")

# 메인 화면 구성
st.title("단어 빈도수 시각화")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if check_btn:
        st.write("데이터 미리보기:")
        st.dataframe(df.head())

    if start_btn:
        counts = ta.get_word_counts(df, column_name)
        
        if counts:
            st.success(f"분석이 완료되었습니다")
            
            col1, col2 = st.columns(2)
            
            if show_bar:
                with col1:
                    fig_bar = vis.create_bar_chart(counts, bar_n)
                    st.pyplot(fig_bar)
            
            if show_wc:
                with col2:
                    fig_wc = vis.create_wordcloud(counts, wc_n)
                    st.pyplot(fig_wc)
        else:
            st.error(f"'{column_name}' 컬럼을 찾을 수 없습니다.")
else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")