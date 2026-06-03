import NaverNewsCrawler as nnc
import streamlit as st
st.header('네이버 뉴스 크롤러')
keyword = st.text_input('검색할 키워드 : ')
sea_btn = st.button('뉴스 크롤링 시작')
save_btn = st.button('CSV 파일로 저장')
if sea_btn and keyword:
    st.session_state.corpus = nnc.crawlMain(keyword)
    st.info(f'{len(st.session_state.corpus)}개의 뉴스 기사가 크롤링되었습니다.')

if save_btn:
    if st.session_state.corpus:
        nnc.saveJsonToCSV(st.session_state.corpus, 'news_corpus.csv')
        st.success('CSV 파일로 저장되었습니다.')
    else:
        st.warning('먼저 뉴스 크롤링을 시작해주세요.')