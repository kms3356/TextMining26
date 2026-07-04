import streamlit as st
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(page_title="IT 기술 스택 연관성 분석", layout="wide")

def parse_skills_from_column(cell_value):
    
    # 타입이 리스트인지 검사해서 처리
    if isinstance(cell_value, list):
        return [str(v).strip().lower() for v in cell_value if v]
        
    if hasattr(cell_value, 'tolist'):
        return [str(v).strip().lower() for v in cell_value.tolist() if v]

    # 단일 값일 때만 결측치 및 빈 문자열 체크 처리
    if pd.isna(cell_value) or str(cell_value).strip() == '':
        return []
        
    # 문자열 형태의 리스트나 텍스트 파싱 로
    val_str = str(cell_value).strip()
    if val_str.startswith('['):
        items = re.findall(r"[a-zA-Z가-힣+#.]+", val_str)
        return [i.lower() for i in items if i]
    else:
        items = re.split(r'[,/·\s]+', val_str)
        return [i.lower() for i in items if i and len(i) >= 1]

@st.cache_data
def load_and_process_data():
    
    # 파일 로드
    with open('../data/extracted_jobs_result_wanted.json', 'r', encoding='utf-8') as f: wanted = json.load(f)
    with open('../data/extracted_jobs_result_jobkorea.json', 'r', encoding='utf-8') as f: jobkorea = json.load(f)
    with open('../data/extracted_jobs_result_saramin.json', 'r', encoding='utf-8') as f: saramin = json.load(f)
    
    df_wanted = pd.DataFrame(wanted)
    df_jobkorea = pd.DataFrame(jobkorea)
    df_saramin = pd.DataFrame(saramin)
    
    # 잡코리아 컬럼명 정규화
    df_jobkorea.columns = df_jobkorea.columns.str.replace(r'\\', '/', regex=True)
    
    TECH_NAME_MAP = {
        'java': 'Java', 'python': 'Python', 'spring': 'Spring', 'springboot': 'Spring Boot',
        'spring boot': 'Spring Boot', 'react': 'React', 'aws': 'AWS', 'docker': 'Docker',
        'kubernetes': 'Kubernetes', 'git': 'Git', 'mysql': 'MySQL', 'oracle': 'Oracle',
        'typescript': 'TypeScript', 'ts': 'TypeScript', 'javascript': 'JavaScript', 'js': 'JavaScript',
        'node.js': 'Node.js', 'nodejs': 'Node.js', 'vue': 'Vue.js', 'vue.js': 'Vue.js',
        'linux': 'Linux', 'c++': 'C++', 'c#': 'C#', 'php': 'PHP', 'html': 'HTML', 'css': 'CSS',
        '시스템개발': '시스템', '시스템분석': '시스템', '시스템설계': '시스템', '시스템운영': '시스템',
        '데이터분석': '데이터', '데이터 분석': '데이터', '서버구축': '서버', '서버관리': '서버', 'ai': 'AI', 
        'excel': '엑셀', 'si': 'SI', 'si개발': 'SI', 'si 개발': 'SI', 
        'MS OFFICE': 'Ms office', 'Ms Office': 'Ms office', 'ms office': 'Ms office', '네트워크관리': '네트워크',
        'gcp': 'GCP', 'ppt': 'PPT', 'crm': 'CRM', 'photoshop': '포토샵', 'http': 'HTTP', 'rdbms': 'RDBMS', 'bigdata': '빅데이터',
        '빅데이터': '빅데이터', 'ci/cd': 'CI/CD', 'C/c++': 'C', 'Restful api': 'Rest api', 'fastapi': 'Fast api',
        'fast api': 'Fast api'
    }
    
    processed_jobs = []
    all_raw_techs = []
    
    # 원티드
    if 'skill_tags' in df_wanted.columns:
        for cell in df_wanted['skill_tags']:
            parsed = parse_skills_from_column(cell)
            
            standardized = []
            for t in parsed:
                t_lower = t.lower()
                if t_lower in TECH_NAME_MAP:
                    standardized.append(TECH_NAME_MAP[t_lower])
                else:
                    standardized.append(t.upper() if len(t) <= 3 else t.capitalize())
            
            # 매핑 사전에 있으면 치환, 없으면 첫글자 대문자화
            unique_list = list(set(standardized))
            processed_jobs.append(unique_list)
            all_raw_techs.extend(unique_list)
    
    # 잡코리아        
    if '기술스택/분야' in df_jobkorea.columns:
        for cell in df_jobkorea['기술스택/분야']:
            parsed = parse_skills_from_column(cell)
            
            standardized = []
            for t in parsed:
                t_lower = t.lower()
                if t_lower in TECH_NAME_MAP:
                    standardized.append(TECH_NAME_MAP[t_lower])
                else:
                    standardized.append(t.upper() if len(t) <= 3 else t.capitalize())
                    
            unique_list = list(set(standardized))
            processed_jobs.append(unique_list)
            all_raw_techs.extend(unique_list)
    
    # 사람인          
    if 'hard_skills' in df_saramin.columns:
        for cell in df_saramin['hard_skills']:
            parsed = parse_skills_from_column(cell)
            
            standardized = []
            for t in parsed:
                t_lower = t.lower()
                if t_lower in TECH_NAME_MAP:
                    standardized.append(TECH_NAME_MAP[t_lower])
                else:
                    standardized.append(t.upper() if len(t) <= 3 else t.capitalize())
                    
            unique_list = list(set(standardized))
            processed_jobs.append(unique_list)
            all_raw_techs.extend(unique_list)
    
    return processed_jobs, all_raw_techs


processed_jobs, all_raw_techs = load_and_process_data()

# 불용어 처리
EXCLUDE_TECH = {
                '소프트웨어개발', '솔루션', 'SI', '시스템', '네트워크', '서버', '시스템', '정보보안', 'Sm', '데이터', 'erp', 
                '문서작성', 'AI', '클라이언트', '유지보수', '방화벽', 'Ms office', '기술지원', '영어', '검증', '모델링', 
                '전략기획', '회로설계', '재고관리', '아키텍처', '매출관리', '인터페이스', 'GUI', 'PPT', 'PM', '회계', '고객관리',
                '핀테크', '모바일앱개발', '문서관리', '보안관제', 'HTTP', '반응형웹', '포토샵'
                } 

# 전체 리스트에서 제외할 단어 필터링
all_raw_techs = [tech for tech in all_raw_techs if tech not in EXCLUDE_TECH]

# 데이터 로드 및 상위 50위 계산
processed_jobs, all_words = load_and_process_data()

# 전체 7개 컬럼 데이터에서 빈도수 TOP 50 추출
top_50_counts = Counter(all_raw_techs).most_common(50)
top_50_skills = [skill for skill, _ in top_50_counts]


st.title("🎯 핵심 기술 스택 기반 연관성 분석 대시보드")
st.markdown("잡코리아, 원티드, 사람인 사이트 추출 결과로 구성된 **상위 50대 기술 필터**입니다.")

st.sidebar.header("🛠️ 기술 스택 필터")
selected_tech = st.sidebar.selectbox(
    "분석할 기술 스택을 선택하세요:",
    top_50_skills # 빈도 순위 정렬 배치
)

st.sidebar.markdown("---")
st.sidebar.write("### 🔥 현재 데이터 내 스택 랭킹 TOP 5")
for i, (tech, cnt) in enumerate(top_50_counts[:5]):
    st.sidebar.write(f"**{i+1}위.** {tech} ({cnt}건)")


# 실시간 연관 기술 계산
related_skills = []
total_matching_jobs = 0

for skills in processed_jobs:
    if selected_tech in skills:
        total_matching_jobs += 1
        for skill in skills:
            # 자기 자신을 제외하고 TOP 50 안에 포함된 다른 핵심 기술만 매칭
            if skill != selected_tech and skill in top_50_skills:
                related_skills.append(skill)

co_occurring_counts = Counter(related_skills)


# 화면 시각화 출력
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 핵심 요약 리포트")
    st.metric(label=f"'{selected_tech}' 데이터 포함 건수", value=f"{total_matching_jobs} 건")
    
    st.write(f"### '{selected_tech}'와 함께 언급된 핵심 연관 순위")
    df_rank = pd.DataFrame(co_occurring_counts.most_common(12), columns=['연관 기술 스택', '동시 출현 빈도'])
    st.dataframe(df_rank, use_container_width=True)

with col2:
    st.subheader(f"☁️ '{selected_tech}' 연관 스택 워드클라우드")
    
    if len(co_occurring_counts) > 0:
        wordcloud = WordCloud(
            font_path='malgun',
            background_color='white',
            width=800,
            height=500,
            colormap='plasma'
        ).generate_from_frequencies(dict(co_occurring_counts))
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning(f"'{selected_tech}'와 동시에 출현한 다른 기술 스택 데이터가 없습니다.")
        
        
# ====================================================================
# 🚨 [콘솔 확인용 코드] 스트림릿이 실행될 때 터미널창에 TOP 100을 출력합니다.
# ====================================================================

# 1. 데이터 기반 필터링 진행 (화면 로드용과 싱크 맞춤)
# 불용어 처리 (대소문자 상관없이 매핑 사전 통과했으므로 표기법에 맞춤)
filtered_techs = [tech for tech in all_raw_techs if tech not in EXCLUDE_TECH]

# 2. TOP 100 추출
top_100 = Counter(filtered_techs).most_common(100)

# 3. 콘솔창에 예쁘게 출력하기
print("\n" + "="*70)
print(f"🚀 [콘솔 단독 확인] 데이터셋 내 기술 스택 빈도수 TOP 100 (총 {len(set(filtered_techs))}개 중)")
print("="*70)

# 2줄씩 보기 좋게 정렬해서 출력 (왼쪽 1~50위, 오른쪽 51~100위 구조로 매칭)
for i in range(50):
    if i >= len(top_100):
        break
        
    # 왼쪽 라인 (1 ~ 50위)
    l_rank = i + 1
    l_name, l_count = top_100[l_rank - 1]
    left_str = f"[{l_rank:2d}위] {l_name:<18} ({l_count:3d}건)"
    
    # 오른쪽 라인 (51 ~ 100위)
    right_str = ""
    if i + 50 < len(top_100):
        r_rank = i + 51
        r_name, r_count = top_100[r_rank - 1]
        right_str = f" 👉   [{r_rank:3d}위] {r_name:<18} ({r_count:3d}건)"
        
    print(f"{left_str}{right_str}")
    
print("="*70)
print("💡 대소문자 통합 및 RDBMS, 빅데이터, 포토샵 변환 규칙이 완벽하게 적용된 결과입니다.\n")