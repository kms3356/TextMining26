from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# --- 설정 ---
TARGET_COUNT = 10000
SAVE_INTERVAL = 500
FILE_NAME = "jobkorea_it_jobs_click_version.csv"

# 페이지 번호를 뺀 기본 URL (처음에 1페이지만 한 번 엽니다)
BASE_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=duty&dutyCtgr=10031"

def save_to_csv(data, filename, is_first_save):
    df = pd.DataFrame(data, columns=['공고번호', '회사명', '공고제목', '기술스택/분야', '마감일'])
    if is_first_save:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(filename, mode='a', index=False, header=False, encoding='utf-8-sig')

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--ignore-certificate-errors")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def main():
    driver = get_chrome_driver()
    total_collected = 0
    page = 1
    current_batch_data = []
    is_first_save = not os.path.exists(FILE_NAME)
    
    seen_job_ids = set()

    print(f"🚀 [클릭 우회 방식] 잡코리아 크롤링 시작! (목표: {TARGET_COUNT}건)")

    try:
        # 1. 처음에만 URL로 접속
        driver.get(BASE_URL)
        time.sleep(3)

        while total_collected < TARGET_COUNT:
            print(f"--- {page}페이지 수집 중... (현재 누적: {total_collected}건) ---")
            
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.post-list-corp, .tplCo, .corp-name, .name'))
                )
            except Exception as e:
                print("⚠️ 페이지 로딩에 실패했습니다.")
                break

            # 현재 화면 파싱
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_list = soup.select('.list-default .list-post, .list-default tbody tr, tbody tr, article.list-item')

            valid_jobs = [job for job in job_list if job.select_one('.post-list-corp a, .tplCo a, .name a')]

            if not valid_jobs:
                break

            for job in valid_jobs:
                if total_collected >= TARGET_COUNT:
                    break
                    
                try:
                    title_tag = job.select_one('.post-list-info a, .tplTit a, .tit a')
                    if not title_tag:
                        continue
                    
                    job_title = title_tag.get('title') or title_tag.text.strip()
                    href = title_tag.get('href', '')
                    job_id = href.split('/')[-1].split('?')[0] if href else 'N/A'

                    if not job_title.strip() or job_id == 'N/A':
                        continue

                    exclude_keywords = ['파견', '헤드헌팅', '헤드헌터', '프리랜서', '도급']
                    if any(keyword in job_title for keyword in exclude_keywords):
                        continue

                    # 중복 검사
                    if job_id in seen_job_ids:
                        continue
                    
                    seen_job_ids.add(job_id)

                    company_tag = job.select_one('.post-list-corp a, .tplCo a, .name a')
                    company_name = company_tag.text.strip() if company_tag else 'N/A'

                    tech_tags = job.select('.post-list-info .option, .tplTit .dsc, .tplTit .option, .desc')
                    tech_stack = " ".join([t.text.strip() for t in tech_tags]).replace('\n', ' ')
                    tech_stack = tech_stack.replace('  ', ' ').strip()
                    if not tech_stack: tech_stack = 'N/A'

                    deadline_tag = job.select_one('.date, .time')
                    deadline = deadline_tag.text.strip() if deadline_tag else 'N/A'

                    current_batch_data.append([job_id, company_name, job_title, tech_stack, deadline])
                    total_collected += 1
                    
                    print(f"✅ [{total_collected}] {company_name} / {job_title[:20]}...")

                except Exception as e:
                    continue

            # 중간 저장
            if len(current_batch_data) >= SAVE_INTERVAL or total_collected >= TARGET_COUNT:
                save_to_csv(current_batch_data, FILE_NAME, is_first_save)
                print(f"💾 {len(current_batch_data)}건 중간 저장 완료! (현재 {total_collected}건)")
                current_batch_data = []
                is_first_save = False

            if total_collected >= TARGET_COUNT:
                break

            # ⭐ 핵심: 마우스로 다음 페이지 번호 직접 클릭하기
            next_page = page + 1
            try:
                # 하단 페이지네이션 영역 찾기
                pagination = driver.find_element(By.CSS_SELECTOR, ".tplPagination, .paging, .list-paging")
                
                # 다음 페이지가 11, 21, 31... 일 때는 '다음' 화살표 버튼 클릭
                if next_page % 10 == 1:
                    next_btn = pagination.find_element(By.XPATH, ".//a[contains(text(), '다음') or contains(@class, 'next')]")
                    driver.execute_script("arguments[0].click();", next_btn)
                else:
                    # 그 외에는 숫자 버튼 클릭
                    page_btn = pagination.find_element(By.XPATH, f".//a[text()='{next_page}']")
                    driver.execute_script("arguments[0].click();", page_btn)
                
                # 버튼을 누른 후 새 데이터가 화면에 그려질 때까지 대기
                time.sleep(random.uniform(2.5, 4.0))
                page = next_page

            except Exception as e:
                print("🛑 마지막 페이지에 도달했거나 더 이상 누를 버튼이 없습니다.")
                break

    finally:
        driver.quit()

        if current_batch_data:
            save_to_csv(current_batch_data, FILE_NAME, is_first_save)
            print(f"💾 남은 {len(current_batch_data)}건 최종 저장 완료!")
            
        print(f"\n🎉 크롤링 완료! 총 {total_collected}건이 '{FILE_NAME}'에 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    main()