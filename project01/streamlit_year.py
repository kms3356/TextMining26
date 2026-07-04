import streamlit as st
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# 한글 폰트 및 마이너스 깨짐 방지 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="연차별 IT 기술 스택 분석", layout="wide", page_icon="📊")

# ==========================================
# 1. 전처리 함수 모음
# ==========================================

def parse_skills_from_column(cell_value):
    if isinstance(cell_value, list):
        return [str(v).strip().lower() for v in cell_value if v]
    if hasattr(cell_value, 'tolist'):
        return [str(v).strip().lower() for v in cell_value.tolist() if v]
    if pd.isna(cell_value) or str(cell_value).strip() == '':
        return []
        
    val_str = str(cell_value).strip()
    if val_str.startswith('['):
        items = re.findall(r"[a-zA-Z가-힣+#.]+", val_str)
        return [i.lower() for i in items if i]
    else:
        items = re.split(r'[,/·\s]+', val_str)
        return [i.lower() for i in items if i and len(i) >= 1]

def fill_and_format_year(row):
    # 원티드 연차 전처리
    if 'year_filter' not in row or 'requirements' not in row:
        return [0.0]
        
    val = row['year_filter']
    if pd.notna(val) and str(val).strip() != '':
        if isinstance(val, list):
            return val
        return [float(val)]
        
    req_text = str(row['requirements']) 
    years = re.findall(r'(\d+)\s*년', req_text)
    
    if years:
        max_year = max([int(y) for y in years])
        if max_year >= 5: return [5.0]
        elif max_year >= 3: return [3.0]
        elif max_year >= 1: return [1.0]
            
    if '신입' in req_text:
        return [0.0]
    return [0.0]

def parse_jobkorea_multi_mapped(exp_str):
    # 잡코리아 연차 전처리
    if pd.isna(exp_str) or str(exp_str).strip() == '':
        return [0.0]

    exp_str = str(exp_str)
    result = set()

    if '신입' in exp_str or '무관' in exp_str:
        result.add(0.0)

    years = re.findall(r'(\d+)년', exp_str)
    
    if years:
        for y in years:
            y_int = int(y)
            if y_int >= 5: result.add(5.0)
            elif y_int >= 3: result.add(3.0)
            elif y_int >= 1: result.add(1.0)
    else:
        if '경력' in exp_str:
            result.add(1.0) 

    if result:
        return sorted(list(result))
    else:
        return [0.0]


# ==========================================
# 2. 데이터 로드 및 병합 (캐싱)
# ==========================================

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

EXCLUDE_TECH = {
    '소프트웨어개발', '솔루션', 'SI', '시스템', '네트워크', '서버', '정보보안', 'Sm', '데이터', 'erp', 
    '문서작성', 'AI', '클라이언트', '유지보수', '방화벽', 'Ms office', '기술지원', '영어', '검증', '모델링', 
    '전략기획', '회로설계', '재고관리', '아키텍처', '매출관리', '인터페이스', 'GUI', 'PPT', 'PM', '회계', '고객관리',
    '핀테크', '모바일앱개발', '문서관리', '보안관제', 'HTTP', '반응형웹', '포토샵'
}

@st.cache_data
def load_and_process_data():
    try:
        with open('./data/extracted_jobs_result_wanted.json', 'r', encoding='utf-8') as f: wanted = json.load(f)
        with open('./data/extracted_jobs_result_jobkorea.json', 'r', encoding='utf-8') as f: jobkorea = json.load(f)
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return pd.DataFrame()
        
    df_wanted = pd.DataFrame(wanted)
    df_jobkorea = pd.DataFrame(jobkorea)
    df_jobkorea.columns = df_jobkorea.columns.str.replace(r'\\', '/', regex=True)
    
    # 1. 연차 데이터 추출
    if 'year_filter' in df_wanted.columns or 'requirements' in df_wanted.columns:
        # fill_and_format_year 함수가 에러나지 않도록 빈 컬럼 생성
        if 'year_filter' not in df_wanted.columns: df_wanted['year_filter'] = None
        if 'requirements' not in df_wanted.columns: df_wanted['requirements'] = ""
        df_wanted['years'] = df_wanted.apply(fill_and_format_year, axis=1)
    else:
        df_wanted['years'] = [[0.0]] * len(df_wanted)
        
    if '연차/경력' in df_jobkorea.columns:
        df_jobkorea['years'] = df_jobkorea['연차/경력'].apply(parse_jobkorea_multi_mapped)
    else:
        df_jobkorea['years'] = [[0.0]] * len(df_jobkorea)

    # 2. 기술 스택 추출 및 표준화 함수
    def get_standardized_techs(series):
        all_parsed = []
        for cell in series:
            parsed = parse_skills_from_column(cell)
            standardized = []
            for t in parsed:
                t_lower = t.lower()
                if t_lower in TECH_NAME_MAP:
                    standardized.append(TECH_NAME_MAP[t_lower])
                else:
                    standardized.append(t.upper() if len(t) <= 3 else t.capitalize())
            
            # 불용어 제거 및 중복 제거
            filtered = list(set([tech for tech in standardized if tech not in EXCLUDE_TECH]))
            all_parsed.append(filtered)
        return all_parsed

    if 'skill_tags' in df_wanted.columns:
        df_wanted['techs'] = get_standardized_techs(df_wanted['skill_tags'])
    else:
        df_wanted['techs'] = [[]] * len(df_wanted)
        
    if '기술스택/분야' in df_jobkorea.columns:
        df_jobkorea['techs'] = get_standardized_techs(df_jobkorea['기술스택/분야'])
    else:
        df_jobkorea['techs'] = [[]] * len(df_jobkorea)

    # 3. 필요 컬럼만 뽑아서 위아래로 병합
    df_w_sub = df_wanted[['years', 'techs']]
    df_j_sub = df_jobkorea[['years', 'techs']]
    df_merged = pd.concat([df_w_sub, df_j_sub], ignore_index=True)

    # 4. 리스트 폭발 (Explode) 
    # [0.0, 3.0], [Java, Spring] -> 4개의 행으로 변환 (0-Java, 0-Spring, 3-Java, 3-Spring)
    df_exploded = df_merged.explode('years').explode('techs')
    
    # 결측치(기술스택이 없는 공고 등) 제거
    df_exploded = df_exploded.dropna(subset=['years', 'techs'])
    
    return df_exploded

# 데이터 로딩
df_master = load_and_process_data()

if df_master.empty:
    st.stop()


# ==========================================
# 3. 화면 UI 구성 및 시각화
# ==========================================

st.title("📈 연차/경력별 기술 스택 트렌드 대시보드")
st.markdown("원티드 및 잡코리아의 채용공고를 분석하여 **요구 경력별로 어떤 기술 스택을 선호하는지** 보여줍니다.")

# 매핑 딕셔너리
YEAR_LABELS = {
    0.0: "🌱 신입/경력무관 (0년)",
    1.0: "🚀 주니어 (1~2년)",
    3.0: "🔥 미들 (3~4년)",
    5.0: "👑 시니어 (5년 이상)"
}

# 사이드바 구성
st.sidebar.header("🎯 필터 옵션")
selected_year_val = st.sidebar.radio(
    "조회할 연차를 선택하세요:",
    options=[0.0, 1.0, 3.0, 5.0],
    format_func=lambda x: YEAR_LABELS[x]
)

# 데이터 필터링
df_filtered = df_master[df_master['years'] == selected_year_val]
total_postings = df_filtered.groupby(level=0).ngroups # 원본 공고 개수 추정 (인덱스 기준)
tech_counts = df_filtered['techs'].value_counts()
top_20_techs = tech_counts.head(20)

st.sidebar.markdown("---")
st.sidebar.metric(label="선택된 연차 매칭 공고 수", value=f"{len(df_filtered)} 건")

# 메인 레이아웃 (2단 구성)
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(f"📊 {YEAR_LABELS[selected_year_val]} - Top 20 기술 스택")
    
    if not top_20_techs.empty:
        # 수평 막대 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 역순 정렬 (가장 큰 값이 위로 오도록)
        top_20_techs_rev = top_20_techs[::-1]
        
        bars = ax.barh(top_20_techs_rev.index, top_20_techs_rev.values, color='#4A90E2', edgecolor='black')
        
        # 바 옆에 숫자 표기
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                    ha='left', va='center', fontsize=10)
            
        ax.set_xlabel('출현 빈도 (건)')
        ax.set_title(f'{YEAR_LABELS[selected_year_val]} 기술 스택 Top 20')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("해당 연차에 대한 데이터가 없습니다.")

with col2:
    st.subheader("☁️ 워드클라우드")
    if not top_20_techs.empty:
        wordcloud = WordCloud(
            font_path='malgun',
            background_color='white',
            width=600,
            height=600,
            colormap='viridis',
            max_words=50
        ).generate_from_frequencies(tech_counts.to_dict())
        
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.imshow(wordcloud, interpolation='bilinear')
        ax2.axis('off')
        st.pyplot(fig2)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("### 🏆 Top 10 리스트")
        df_rank = pd.DataFrame({'기술 스택': tech_counts.head(10).index, '건수': tech_counts.head(10).values})
        df_rank.index = df_rank.index + 1
        st.dataframe(df_rank, use_container_width=True)
        
    else:
        st.info("시각화할 데이터가 부족합니다.")

# ====================================================================
# [하단] 전체 연차 비교 차트 (Bonus)
# ====================================================================
st.markdown("---")
st.subheader("💡 연차별 핵심 기술 스택 비교 (상위 5개)")

# 전체 연차에서 가장 많이 등장한 Top 5 기술 추출
global_top_5 = df_master['techs'].value_counts().head(5).index

# 연차별, 기술별 카운트를 구한 뒤 Pivot Table로 변환
df_pivot = df_master[df_master['techs'].isin(global_top_5)].groupby(['years', 'techs']).size().unstack(fill_value=0)

if not df_pivot.empty:
    # 인덱스 이름 변경
    df_pivot.index = [YEAR_LABELS[y].split(' ')[1] for y in df_pivot.index]
    
    st.bar_chart(df_pivot)
else:
    st.write("비교할 데이터가 충분하지 않습니다.")