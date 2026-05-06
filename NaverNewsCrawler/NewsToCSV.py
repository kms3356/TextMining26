import NaverNewsCrawler as nnc
keyword = input('검색할 키워드 : ')
corpus = nnc.crawlMain(keyword)
res = ''.join(cur['title'] + cur['description'] for cur in corpus)
