import streamlit as st
import pandas as pd
import json
import re
from collections import Counter
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import requests
import os
from dotenv import load_dotenv

# 현재 실행 중인 파일의 경로를 기준으로 상위 폴더의 .env 경로 계산
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '..', '.env')

# .env 파일 로드
load_dotenv(dotenv_path)

# 환경 변수 불러오기
KAKAO_API_KEY = os.environ.get("KAKAO_API_KEY")

if KAKAO_API_KEY:
    print("카카오 API 키를 성공적으로 불러왔습니다.")
else:
    print("API 키를 찾을 수 없습니다. 경로를 다시 확인해주세요.")

current_dir
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
    return list(set([tech for tech in standardized if tech not in EXCLUDE_TECH]))

# --- 2. 카카오 API 연동 위경도 변환 함수 ---
# --- 2. 카카오 API 연동 위경도 변환 함수 (디버깅 추가) ---
@st.cache_data
def get_coordinates_dict(locations, api_key):
    coords_dict = {}
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    
    for loc in locations:
        if loc == '원격근무' or not loc:
            continue
            
        try:
            response = requests.get(url, headers=headers, params={'query': loc})
            
            # API 호출이 실패(401 권한 없음 등)했을 경우 에러 출력
            if response.status_code != 200:
                st.error(f"API 에러 발생: {response.status_code} - {response.text}")
                break # 에러가 나면 반복문 중단
                
            result = response.json()
            if result.get('documents'):
                y = float(result['documents'][0]['y']) 
                x = float(result['documents'][0]['x']) 
                coords_dict[loc] = [y, x]
        except Exception as e:
            st.error(f"좌표 변환 중 오류: {e}")
            
    return coords_dict

# --- 3. 데이터 로드 및 병합 ---
@st.cache_data
def load_and_merge_data():
    with open('wanted_clean_location.json', 'r', encoding='utf-8') as f: wanted = json.load(f)
    with open('jobkorea_clean_location.json', 'r', encoding='utf-8') as f: jobkorea = json.load(f)
    
    df_wanted = pd.DataFrame(wanted)
    df_jobkorea = pd.DataFrame(jobkorea)
    df_jobkorea.columns = df_jobkorea.columns.str.replace(r'\\', '/', regex=True)

    df_wanted['techs'] = df_wanted['skill_tags'].apply(standardize_techs) if 'skill_tags' in df_wanted.columns else [[]] * len(df_wanted)
    df_jobkorea['techs'] = df_jobkorea['기술스택/분야'].apply(standardize_techs) if '기술스택/분야' in df_jobkorea.columns else [[]] * len(df_jobkorea)

    df_wanted['location'] = df_wanted['location_perfect'] if 'location_perfect' in df_wanted.columns else "서울 강남구" 
    df_jobkorea['location'] = df_jobkorea['location_clean'] if 'location_clean' in df_jobkorea.columns else "서울 서초구"

    df_master = pd.concat([
        df_wanted[['location', 'techs']], 
        df_jobkorea[['location', 'techs']]
    ], ignore_index=True)
    
    df_master = df_master.dropna(subset=['location'])
    
    # 데이터셋에 존재하는 고유한 지역명만 추출하여 API 한 번에 호출 (속도 최적화)
    unique_locations = df_master['location'].unique()
    
    # API 키가 입력되어 있을 때만 실행
    if KAKAO_API_KEY != "YOUR_KAKAO_REST_API_KEY":
        dynamic_coords = get_coordinates_dict(unique_locations, KAKAO_API_KEY)
    else:
        # 키가 없으면 임시로 서울 중심 좌표로 매핑 (경고 표시용)
        dynamic_coords = {}
    
    # 좌표 매핑 (좌표를 못 찾은 지역은 None 처리)
    df_master['lat'] = df_master['location'].apply(lambda x: dynamic_coords.get(x, [None, None])[0])
    df_master['lon'] = df_master['location'].apply(lambda x: dynamic_coords.get(x, [None, None])[1])
    
    return df_master

df_master = load_and_merge_data()

# --- 4. 지역별 집계 (좌표가 있는 곳만 필터링) ---
# 좌표가 없는 데이터(예: 원격근무, API 실패) 제외하여 지도 렌더링 에러 방지
df_map = df_master.dropna(subset=['lat', 'lon'])

region_group = df_map.groupby('location').agg({
    'techs': 'sum',
    'lat': 'first',      
    'lon': 'first'
}).reset_index()

region_group['job_count'] = df_map.groupby('location').size().values

# --- 5. UI 구성 ---
st.title("📍 대한민국 IT 기술 스택 지역 분포도")

# API 키가 없으면 경고 메시지 출력
if KAKAO_API_KEY == "YOUR_KAKAO_REST_API_KEY":
    st.warning("⚠️ 코드 상단의 `KAKAO_API_KEY`에 카카오 REST API 키를 입력해야 지도가 정상적으로 표시됩니다.")

st.markdown("지도에 표시된 **파란색 마커**를 클릭하면 해당 지역의 핵심 기술 스택 트렌드가 우측에 나타납니다.")

col_map, col_details = st.columns([1.5, 1])

if 'selected_region' not in st.session_state:
    st.session_state['selected_region'] = None
st.write("📍 마커 데이터 확인:", region_group)
with col_map:
    # 대한민국 중심 좌표 설정
    m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB positron')
    
    for idx, row in region_group.iterrows():
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
    
    map_data = st_folium(m, height=600, use_container_width=True)
    
    if map_data['last_object_clicked_popup'] is not None:
        st.session_state['selected_region'] = map_data['last_object_clicked_popup']

with col_details:
    clicked_region = st.session_state['selected_region']
    
    if clicked_region:
        st.subheader(f"🏢 {clicked_region} 상세 분석")
        
        region_data = region_group[region_group['location'] == clicked_region]
        
        if not region_data.empty:
            techs_list = region_data.iloc[0]['techs']
            job_count = region_data.iloc[0]['job_count']
            
            st.metric(label="해당 지역 공고 수", value=f"{job_count} 건")
            
            tech_counter = Counter(techs_list)
            
            # 남길 키워드 (2번 이상)
            filtered_tech_counter = Counter({tech: count for tech, count in tech_counter.items() if count >= 2})
            
            # 💡 [추가] 날아가는 키워드 수집 및 콘솔 출력
            discarded_region_techs = {tech: count for tech, count in tech_counter.items() if count < 2}
            print(f"\n[{clicked_region}] 빈도수 미달로 제외된 키워드 ({len(discarded_region_techs)}개):")
            print(discarded_region_techs)
            
            if filtered_tech_counter:
                st.write("### 🔥 TOP 10 요구 스택")
                df_top_techs = pd.DataFrame(filtered_tech_counter.most_common(10), columns=['기술 스택', '빈도수'])
                df_top_techs = pd.DataFrame(tech_counter.most_common(10), columns=['기술 스택', '빈도수'])
                df_top_techs.index = df_top_techs.index + 1
                
                st.dataframe(df_top_techs, use_container_width=True)
                
                fig, ax = plt.subplots(figsize=(6, 4))
                df_top_techs.sort_values(by='빈도수', ascending=True).plot.barh(x='기술 스택', y='빈도수', ax=ax, color='#ff9f43')
                ax.set_title(f"{clicked_region} 스택 순위")
                st.pyplot(fig)
            else:
                st.info("이 지역에는 추출된 기술 스택이 없습니다.")
    else:
        st.info("👈 지도에서 지역 마커를 클릭하여 상세 정보를 확인하세요.")
        st.subheader("🌐 전국 통합 핵심 스택 TOP 5")
        
        # '원격근무' 데이터도 포함하여 전체 데이터 기준으로 집계
        all_techs = df_master['techs'].sum()
        tech_counts = Counter(all_techs)
        
        # 남길 키워드 (3번 이상)
        filtered_techs = {tech: count for tech, count in tech_counts.items() if count >= 3}
        
        # 💡 [추가] 날아가는 키워드 수집 및 콘솔 출력
        discarded_techs = {tech: count for tech, count in tech_counts.items() if count < 3}
        print(f"\n[전국] 빈도수 미달로 제외된 키워드 ({len(discarded_techs)}개):")
        print(discarded_techs)
        
        top5 = pd.DataFrame(Counter(filtered_techs).most_common(5), columns=['기술', '건수'])
        st.dataframe(top5, use_container_width=True)