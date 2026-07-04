import streamlit as st
import pandas as pd
import json
from collections import Counter
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import requests

# --- 페이지 설정 및 폰트 ---
st.set_page_config(page_title="지역별 IT 기술 스택 지도", layout="wide", page_icon="🗺️")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
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

# 💡 전처리 함수(TECH_NAME_MAP 등)는 노트북에서 이미 완료했으므로 전부 삭제! 앱 속도 대폭 향상!

# --- 1. 카카오 API 연동 위경도 변환 함수 ---
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
            
            if response.status_code != 200:
                st.error(f"API 에러 발생: {response.status_code} - {response.text}")
                break 
                
            result = response.json()
            if result.get('documents'):
                y = float(result['documents'][0]['y']) 
                x = float(result['documents'][0]['x']) 
                coords_dict[loc] = [y, x]
        except Exception as e:
            st.error(f"좌표 변환 중 오류: {e}")
            
    return coords_dict

# --- 2. 데이터 로드 및 병합 ---
@st.cache_data
def load_and_merge_data():
    # 💡 노트북에서 정제 완료한 파일명으로 변경 (예: wanted_cleaned_techs.json)
    file_name = 'wanted_cleaned_techs.json' 
    
    try:
        with open(file_name, 'r', encoding='utf-8') as f: 
            wanted = json.load(f)
    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return pd.DataFrame()

    df_master = pd.DataFrame(wanted)

    # 💡 정제 완료된 'location_final'과 'cleaned_techs' 컬럼을 지도용 컬럼으로 매핑
    df_master['location'] = df_master['location_final']
    df_master['techs'] = df_master['cleaned_techs']
    
    df_master = df_master.dropna(subset=['location'])
    
    # 데이터셋에 존재하는 고유한 지역명만 추출하여 API 호출 (속도 최적화)
    unique_locations = df_master['location'].unique()
    
    if KAKAO_API_KEY != "YOUR_KAKAO_REST_API_KEY" and KAKAO_API_KEY.strip() != "":
        dynamic_coords = get_coordinates_dict(unique_locations, KAKAO_API_KEY)
    else:
        dynamic_coords = {}
    
    # 좌표 매핑 (좌표를 못 찾은 지역은 None 처리)
    df_master['lat'] = df_master['location'].apply(lambda x: dynamic_coords.get(x, [None, None])[0])
    df_master['lon'] = df_master['location'].apply(lambda x: dynamic_coords.get(x, [None, None])[1])
    
    return df_master

df_master = load_and_merge_data()

# --- 3. 지역별 집계 (좌표가 있는 곳만 필터링) ---
if not df_master.empty:
    df_map = df_master.dropna(subset=['lat', 'lon'])

    region_group = df_map.groupby('location').agg({
        'techs': 'sum',
        'lat': 'first',      
        'lon': 'first'
    }).reset_index()

    region_group['job_count'] = df_map.groupby('location').size().values

# --- 4. UI 구성 ---
st.title("📍 대한민국 IT 기술 스택 지역 분포도 (Wanted)")

if KAKAO_API_KEY == "YOUR_KAKAO_REST_API_KEY" or KAKAO_API_KEY.strip() == "":
    st.warning("⚠️ 코드 상단의 `KAKAO_API_KEY`에 카카오 REST API 키를 입력해야 지도가 정상적으로 표시됩니다.")

st.markdown("지도에 표시된 **파란색 마커**를 클릭하면 해당 지역의 핵심 기술 스택 트렌드가 우측에 나타납니다.")

col_map, col_details = st.columns([1.5, 1])

if 'selected_region' not in st.session_state:
    st.session_state['selected_region'] = None

if not df_master.empty:
    with col_map:
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
                
                discarded_region_techs = {tech: count for tech, count in tech_counter.items() if count < 2}
                print(f"\n[{clicked_region}] 빈도수 미달로 제외된 키워드 ({len(discarded_region_techs)}개):")
                print(discarded_region_techs)
                
                if filtered_tech_counter:
                    st.write("### 🔥 TOP 10 요구 스택")
                    # 💡 버그 수정: 위에서 기껏 필터링해놓고 덮어씌우던 문제 해결!
                    df_top_techs = pd.DataFrame(filtered_tech_counter.most_common(10), columns=['기술 스택', '빈도수'])
                    df_top_techs.index = df_top_techs.index + 1
                    
                    st.dataframe(df_top_techs, use_container_width=True)
                    
                    fig, ax = plt.subplots(figsize=(6, 4))
                    df_top_techs.sort_values(by='빈도수', ascending=True).plot.barh(x='기술 스택', y='빈도수', ax=ax, color='#ff9f43')
                    ax.set_title(f"{clicked_region} 스택 순위")
                    st.pyplot(fig)
                else:
                    st.info("이 지역에는 2회 이상 추출된 기술 스택이 없습니다.")
        else:
            st.info("👈 지도에서 지역 마커를 클릭하여 상세 정보를 확인하세요.")
            st.subheader("🌐 전국 통합 핵심 스택 TOP 5")
            
            all_techs = df_master['techs'].sum()
            tech_counts = Counter(all_techs)
            
            filtered_techs = {tech: count for tech, count in tech_counts.items() if count >= 3}
            
            discarded_techs = {tech: count for tech, count in tech_counts.items() if count < 3}
            print(f"\n[전국] 빈도수 미달로 제외된 키워드 ({len(discarded_techs)}개):")
            print(discarded_techs)
            
            top5 = pd.DataFrame(Counter(filtered_techs).most_common(5), columns=['기술', '건수'])
            top5.index = top5.index + 1
            st.dataframe(top5, use_container_width=True)