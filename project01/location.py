import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# --- 페이지 설정 및 폰트 ---
st.set_page_config(page_title="지역별 IT 기술 스택 지도", layout="wide", page_icon="🗺️")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# --- 1. 기술 스택 전처리 환경 ---
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
    'gcp': 'GCP', 'ppt': 'PPT', 'crm': 'CRM', 'photoshop': '포토샵', 'http': 'HTTP', 'rdbms': 'RDBMS', 
    'bigdata': '빅데이터', '빅데이터': '빅데이터', 'ci/cd': 'CI/CD', 'C/c++': 'C', 'Restful api': 'Rest api', 
    'fastapi': 'Fast api', 'fast api': 'Fast api'
}

EXCLUDE_TECH = {
    '소프트웨어개발', '솔루션', 'SI', '시스템', '네트워크', '서버', '정보보안', 'Sm', '데이터', 'erp', 
    '문서작성', 'AI', '클라이언트', '유지보수', '방화벽', 'Ms office', '기술지원', '영어', '검증', '모델링', 
    '전략기획', '회로설계', '재고관리', '아키텍처', '매출관리', '인터페이스', 'GUI', 'PPT', 'PM', '회계', '고객관리',
    '핀테크', '모바일앱개발', '문서관리', '보안관제', 'HTTP', '반응형웹', '포토샵'
}

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

def standardize_techs(cell_value):
    parsed = parse_skills_from_column(cell_value)
    standardized = []
    for t in parsed:
        t_lower = t.lower()
        if t_lower in TECH_NAME_MAP:
            standardized.append(TECH_NAME_MAP[t_lower])
        else:
            standardized.append(t.upper() if len(t) <= 3 else t.capitalize())
    # 불용어 제거 및 중복 제거
    return list(set([tech for tech in standardized if tech not in EXCLUDE_TECH]))

# --- 2. 임시 지역 좌표 사전 (필요시 추가) ---
# 실제 환경에서는 Kakao/Naver Geocoding API를 사용하여 변환하는 것을 권장합니다.
COORDS_MAP = {
    '서울 강남구': [37.4959, 127.0664], '서울 서초구': [37.4769, 127.0378],
    '서울 송파구': [37.5048, 127.1144], '서울 구로구': [37.4954, 126.8581],
    '서울 마포구': [37.5622, 126.9087], '경기 성남시': [37.4386, 127.1378],
    '경기 성남시 분당구': [37.3827, 127.1189], '서울 영등포구': [37.5259, 126.8963],
    '서울 중구': [37.5579, 126.9941], '서울 성동구': [37.5500, 127.0414],
    '인천 연수구': [37.4101, 126.6782], '경기 파주시': [37.7663, 126.7766],
    '대전 서구': [36.3553, 127.3837], '부산 해운대구': [35.1631, 129.1636],
    '서울 종로구': [37.5802, 126.9832], '경기 수원시': [37.2801, 127.0101]
}

# --- 3. 데이터 로드 및 병합 ---
@st.cache_data
def load_and_merge_data():
    # 데이터 로드 (경로는 실제 환경에 맞게 수정)
    with open('wanted_clean_location.json', 'r', encoding='utf-8') as f: wanted = json.load(f)
    with open('jobkorea_clean_location.json', 'r', encoding='utf-8') as f: jobkorea = json.load(f)
    
    df_wanted = pd.DataFrame(wanted)
    df_jobkorea = pd.DataFrame(jobkorea)
    df_jobkorea.columns = df_jobkorea.columns.str.replace(r'\\', '/', regex=True)

    # 1. 기술 스택 파싱 및 정제
    df_wanted['techs'] = df_wanted['skill_tags'].apply(standardize_techs) if 'skill_tags' in df_wanted.columns else [[]] * len(df_wanted)
    df_jobkorea['techs'] = df_jobkorea['기술스택/분야'].apply(standardize_techs) if '기술스택/분야' in df_jobkorea.columns else [[]] * len(df_jobkorea)

    # 2. 지역 데이터 할당 (질문자님이 정제하신 데이터를 불러온다고 가정)
    # 실제로는 사전에 저장해둔 location_perfect, location_clean CSV/JSON을 불러와 매핑해야 합니다.
    # 여기서는 컬럼이 있다고 가정합니다.
    df_wanted['location'] = df_wanted['location_perfect'] if 'location_perfect' in df_wanted.columns else "서울 강남구" 
    df_jobkorea['location'] = df_jobkorea['location_clean'] if 'location_clean' in df_jobkorea.columns else "서울 서초구"

    # 3. 데이터 병합
    df_master = pd.concat([
        df_wanted[['location', 'techs']], 
        df_jobkorea[['location', 'techs']]
    ], ignore_index=True)
    
    # 결측치 제거
    df_master = df_master.dropna(subset=['location'])
    
    # 4. 좌표 매핑 (좌표 사전에 없으면 기본값 서울시청 배정)
    df_master['lat'] = df_master['location'].apply(lambda x: COORDS_MAP.get(x, [37.5665, 126.9780])[0])
    df_master['lon'] = df_master['location'].apply(lambda x: COORDS_MAP.get(x, [37.5665, 126.9780])[1])
    
    return df_master

df_master = load_and_merge_data()

# --- 4. 지역별 집계 ---
# 지역별로 그룹화하여 공고 수와 기술 스택 리스트를 합칩니다.
region_group = df_master.groupby('location').agg({
    'techs': 'sum',      # 해당 지역의 모든 기술 스택 리스트를 하나로 합침
    'lat': 'first',      
    'lon': 'first'
}).reset_index()

region_group['job_count'] = df_master.groupby('location').size().values

# --- 5. UI 구성 ---
st.title("📍 대한민국 IT 기술 스택 지역 분포도")
st.markdown("지도에 표시된 **파란색 마커**를 클릭하면 해당 지역의 핵심 기술 스택 트렌드가 우측에 나타납니다.")

col_map, col_details = st.columns([1.5, 1])

# 선택된 지역 상태 저장
if 'selected_region' not in st.session_state:
    st.session_state['selected_region'] = None

with col_map:
    # Folium 지도 생성 (대한민국 중심 좌표)
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB positron')
    
    # 지역별 마커 추가
    for idx, row in region_group.iterrows():
        # 마커 크기를 공고 수에 비례하게 설정
        radius = min(max(row['job_count'] * 0.2, 5), 30) 
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color='#4A90E2',
            fill=True,
            fill_color='#4A90E2',
            fill_opacity=0.6,
            tooltip=f"{row['location']} (공고 {row['job_count']}건)"
        ).add_child(folium.Popup(row['location'])).add_to(m)
    
    # 지도를 Streamlit에 렌더링하고 클릭 이벤트 데이터 받기
    map_data = st_folium(m, height=600, use_container_width=True)
    
    # 사용자가 마커를 클릭했을 때 지역명 추출
    if map_data['last_object_clicked_popup'] is not None:
        st.session_state['selected_region'] = map_data['last_object_clicked_popup']

with col_details:
    clicked_region = st.session_state['selected_region']
    
    if clicked_region:
        st.subheader(f"🏢 {clicked_region} 상세 분석")
        
        # 선택된 지역 데이터 추출
        region_data = region_group[region_group['location'] == clicked_region]
        
        if not region_data.empty:
            techs_list = region_data.iloc[0]['techs']
            job_count = region_data.iloc[0]['job_count']
            
            st.metric(label="총 수집된 공고 수", value=f"{job_count} 건")
            
            # 기술 스택 빈도수 계산
            tech_counter = Counter(techs_list)
            if tech_counter:
                st.write("### 🔥 TOP 10 요구 스택")
                df_top_techs = pd.DataFrame(tech_counter.most_common(10), columns=['기술 스택', '빈도수'])
                df_top_techs.index = df_top_techs.index + 1
                
                # 시각적으로 예쁜 데이터프레임 출력
                st.dataframe(df_top_techs, use_container_width=True)
                
                # 간단한 바 차트 추가
                fig, ax = plt.subplots(figsize=(6, 4))
                df_top_techs.sort_values(by='빈도수', ascending=True).plot.barh(x='기술 스택', y='빈도수', ax=ax, color='#ff9f43')
                ax.set_title(f"{clicked_region} 스택 순위")
                st.pyplot(fig)
            else:
                st.info("이 지역에는 추출된 기술 스택이 없습니다.")
    else:
        # 클릭 전 기본 화면
        st.info("👈 지도에서 지역 마커를 클릭하여 상세 정보를 확인하세요.")
        
        # 전체 데이터 기준 TOP 5를 보여줌
        st.subheader("🌐 전국 통합 핵심 스택 TOP 5")
        all_techs = df_master['techs'].sum()
        top5 = pd.DataFrame(Counter(all_techs).most_common(5), columns=['기술', '건수'])
        st.dataframe(top5, use_container_width=True)