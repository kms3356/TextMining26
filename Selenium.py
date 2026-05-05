from selenium import webdriver
from selenium.webdriver.common.by import By

# 1. 브라우저 실행
driver = webdriver.Chrome()

# 2. 페이지 이동
driver.get("https://www.naver.com")
 
driver.execute_script('script_string')  # 자바스크립트 실행 예시 (필요한 경우)
html_doc = driver.page_source  # 현재 페이지의 HTML 소스 가져오기

# 3. 동작 수행 (예: 검색창에 단어 입력 후 엔터)
search_box = driver.find_element(By.ID, "query")
search_box.send_keys("파이썬")
search_box.submit()
input("Press Enter to continue...")  # 결과를 확인할 시간을 줌
# 4. 브라우저 종료
# driver.quit()