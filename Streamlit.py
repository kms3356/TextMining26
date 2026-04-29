import streamlit as st
import pandas as pd
import time

@st.cache_data # 상호작용만해도 전체를 다시실행하기 때문에 decorator 추가해서 캐시로 함수 결과 저장
def change_text():
    text = st.subheader('변화하는 텍스트') # streamlit 함수 결과를 변수로 지정하면 객체가됨. 원래 title내용이 있던자리에 덮어쓰기 가능.
    time.sleep(2)
    text.info('2초가 지났습니다.')

st.title("Hello, Streamlit World") # 메인제목
tab1, tab2, tab3, tab4 = st.tabs(['1', '2', '3', '4']) # 정보가 많을때 탭 만들어서 화면 전환 가능
with tab1:

    col1, col2, col3 = st.columns(3) # 화면창 세로로 분할해서 병행 표시
    with col1:
        st.header('Header', divider='rainbow') # 섹션 헤더. divider로 구분선 지정가능
        st.subheader('subheader', divider='blue') # 서브 헤더
        st.text('text') # 일반 텍스트
        st.caption('caption') # 설명이나 출처, 각주
        py_code = """def hello():
    print('code')"""
        st.code(py_code, language='python') # 코드블록
        # latex : 수학공식출력. 근의 공식 예시
        st.latex(r'''
            latex = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
        ''')
        
    with col2:
        st.header('DataFrame', divider='red')
        st.subheader('pandas', divider='blue')
        df = pd.DataFrame({'A':[1,2,3,4], 'B':[10,20,30,40]})
        df # Magic Command로 그냥 변수만 써도 st.write() 처리돼서 화면에 출력 됨
        st.subheader('streamlit', divider='blue')
        st.dataframe(df, use_container_width=True, hide_index=True, width=500, height=250, column_order=("B","A")) # 프레임 양식 변경

    with col3:
        st.header('Massage', divider='red')
        st.info('info') # 정보메시지 (Blue) 사용자 안내용
        st.warning('warning') # 성공메시지 (Green) 작업완료 알림
        st.success('success') # 경고메시지 (Yellow) 주의사항
        st.error('error') # 오류메시지 (Red) 에러발생
        change_text()
with tab2:
    st.header('Input', divider='red')
    st.button('button') # 클릭 여부
    st.radio('radio', ['hi', '안녕', '안녕하세요']) # 라디오버튼
    st.checkbox('checkbox') # 체크박스
    st.selectbox('selectbox', ['hi', '안녕', '안녕하세요']) # 드롭다운
    st.multiselect('multiselect', ['hi', '안녕', '안녕하세요']) # 드롭다운 다중선택 가능
    st.slider('slider',0,10,5,1) # start, end, default, step
    st.text_input('텍스트 입력')
    st.number_input('숫자 입력')
    
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        with st.form('my_form'): # form 안에서 함수 사용하면 네모로 묶임
            st.subheader('사용자 정보 입력', divider='yellow')
            name = st.text_input('이름', placeholder='이름을 입력하세요')
            age = st.number_input('나이', value=20, min_value=0, step=1)
            agree = st.checkbox('약관에 동의합니다.')
            with st.expander("사용방법"): # 제목만 노출시키고 클릭해야 세부내용 확인 가능
                st.write("""
                        1. 이름과 나이를 입력하세요.
                        2. 약관동의 버튼을 누르세요.
                        3. submit버튼을 누르시면 제출됩니다.""")
            submitted = st.form_submit_button('submit')
            if name and age and submitted:
                if agree:
                    st.text(f'이름: {name}, 나이: {age}')
                    st.success('약관에 동의했습니다.')
                else: st.error('약관에 동의하세요.')
        
    with col2:
        st.subheader('Matplotlib', divider='yellow')
        st.sidebar.text_input('이름 입력') # st.sidebar.함수명() 하면 화면 왼쪽에 사이드바 배치 가능
        st.sidebar.slider('나이', 0,120,25,1)
        st.sidebar.selectbox('좋아하는 색상 선택', ['빨강', '노랑', '파랑', '초록'])
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots() #
        x = [1,2,3,4]
        y = [5,6,7,8]
        ax.barh(x,y)
        st.pyplot(fig)

with tab4:
    # 강조하고싶은 숫자 변화 출력
    st.header('Metric', divider='green')
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="문제", value="100개", delta="12개 (전일대비)") 
    with col2:
    # 정확도 지표 (delta_color로 색상 반전 가능)
        st.metric(label="정확도", value="98.5%", delta="-0.2% (전일대비)")
    
    # 파일 업로드. 이미지나 csv데이터를 서버로 전달
    st.header('Upload', divider='green')
    uploaded_file = st.file_uploader("이미지를 업로드하세요", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        # 업로드된 이미지를 화면에 보여주기
        st.image(uploaded_file, caption="업로드된 이미지")
        st.success("파일 업로드 완료!")
    
    # 데이터 유지장치. 조작 시 코드초기화하는 단점 극복. 로그인 여부 저장, 누적계산기, 페이지 전환 상태 유지. 딕셔너리 처럼 작동함.
    # 1. 초기값 설정 (없을 경우에만 생성)
    st.header('Session_state', divider='green')
    if 'count' not in st.session_state:
        st.session_state['count'] = 0

    # 2. 값 수정
    if st.button("문제 추가"):
        st.session_state['count'] += 1

    # 3. 값 사용
    st.write(f"현재 등록된 문제: {st.session_state['count']}개")

    st.header('Spinner&Progress', divider='green')
    if st.button("AI 분석 시작"):
        # 스피너: 연산이 끝날 때까지 화면에 떠 있음
        with st.spinner('AI가 이미지에서 글자를 추출하고 있습니다...'):
            # 프로그레스 바: 진행 상황 시각화
            my_bar = st.progress(0)
            
            for percent_complete in range(100):
                time.sleep(0.02) # AI 처리 시간 시뮬레이션
                my_bar.progress(percent_complete + 1)
                
        st.success("분석이 완료되었습니다!")
    st.header('Echo', divider='green')
    with st.echo():
        # 이 안에 작성된 코드는 화면에 텍스트로도 출력되고, 실제로 실행도 됩니다.
        st.write("이 문구는 코드와 함께 화면에 나타납니다.")
        
        def get_user_name():
            return "Streamlit User"
        
        name = get_user_name()
        st.success(f"반갑습니다, {name}님!")