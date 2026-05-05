import NaverNewsCrawler as nnc
import streamlit as st
keyword = input('검색할 키워드 : ')
corpus = nnc.crawlMain(keyword)
res = ''.join(cur['title'] + cur['description'] for cur in corpus)
print(res)
