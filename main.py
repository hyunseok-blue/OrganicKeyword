import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import requests
import time
import json
import os
from datetime import datetime, date
from io import BytesIO
import hashlib

# 페이지 설정
st.set_page_config(
    page_title="네이버 오가닉 키워드 분석기",
    page_icon="🔍",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 모든 테마에서 잘 보이는 중립적 디자인 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* 사이드바 - 모든 테마에서 잘 보이도록 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] h2 {
        color: white !important;
    }
    
    /* 입력창 디자인 - 모든 테마 호환 */
    .stTextInput > div > div > input {
        background: rgba(107, 115, 255, 0.05);
        border: 2px solid rgba(107, 115, 255, 0.3);
        border-radius: 12px;
        padding: 14px 20px;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: inherit;
    }
    .stTextInput > div > div > input:focus {
        background: rgba(107, 115, 255, 0.1);
        border-color: #6B73FF;
        box-shadow: 0 0 0 4px rgba(107, 115, 255, 0.1);
        outline: none;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(107, 115, 255, 0.6);
    }
    
    /* 사이드바 입력창 */
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.15);
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.2);
        border-color: white;
        box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1);
    }
    section[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* 버튼 디자인 - 그라디언트 */
    .stButton > button {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 600;
        font-size: 16px;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(107, 115, 255, 0.4);
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(107, 115, 255, 0.6);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* 메트릭 카드 - 라이트/다크 모드 호환 */
    .metric-card {
        background: linear-gradient(135deg, rgba(107, 115, 255, 0.1) 0%, rgba(0, 13, 255, 0.05) 100%);
        padding: 30px;
        border-radius: 16px;
        margin: 15px 0;
        border: 1px solid rgba(107, 115, 255, 0.2);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, transparent 0%, rgba(107, 115, 255, 0.1) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(107, 115, 255, 0.4);
        box-shadow: 0 12px 32px rgba(107, 115, 255, 0.2);
    }
    .metric-card h3 {
        font-size: 3em;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .metric-card p {
        font-size: 1.1em;
        margin-top: 8px;
        font-weight: 500;
        opacity: 0.7;
    }
    
    /* 결과 카드 - 모던 디자인 */
    .result-card {
        background: linear-gradient(to right, rgba(107, 115, 255, 0.05) 0%, transparent 100%);
        padding: 24px;
        border-radius: 12px;
        margin: 12px 0;
        border: 1px solid rgba(107, 115, 255, 0.15);
        border-left: 4px solid #6B73FF;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .result-card:hover {
        transform: translateX(8px);
        background: linear-gradient(to right, rgba(107, 115, 255, 0.1) 0%, transparent 100%);
        border-color: rgba(107, 115, 255, 0.3);
        box-shadow: 0 8px 24px rgba(107, 115, 255, 0.15);
    }
    .result-card h4 {
        margin: 0 0 12px 0;
        font-weight: 600;
        font-size: 1.1em;
    }
    .result-card p {
        margin: 6px 0;
        font-size: 0.95em;
        opacity: 0.8;
        line-height: 1.5;
    }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(107, 115, 255, 0.05);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: inherit;
        opacity: 0.7;
    }
    .stTabs [data-baseweb="tab"]:hover {
        opacity: 1;
        background: rgba(107, 115, 255, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        opacity: 1;
    }
    
    /* 프로그레스 바 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6B73FF 0%, #000DFF 100%);
        height: 6px;
        border-radius: 3px;
    }
    .stProgress > div > div {
        background: rgba(107, 115, 255, 0.2);
        border-radius: 3px;
        height: 6px;
    }
    
    /* 헤더 타이틀 */
    h1 {
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    h2 {
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    h3 {
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    /* 에러/성공 메시지 */
    .stAlert {
        border-radius: 12px;
        border: 1px solid rgba(107, 115, 255, 0.2);
        background-color: rgba(107, 115, 255, 0.05);
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 600;
        font-size: 16px;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 107, 107, 0.6);
    }
    
    /* 숫자 입력 */
    .stNumberInput > div > div > input {
        background: rgba(107, 115, 255, 0.05);
        border: 2px solid rgba(107, 115, 255, 0.3);
        border-radius: 12px;
        padding: 14px 20px;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stNumberInput > div > div > input:focus {
        background: rgba(107, 115, 255, 0.1);
        border-color: #6B73FF;
        box-shadow: 0 0 0 4px rgba(107, 115, 255, 0.1);
    }
    
    /* 선택 박스 */
    .stSelectbox > div > div {
        background: rgba(107, 115, 255, 0.05);
        border-radius: 12px;
        border: 2px solid rgba(107, 115, 255, 0.3);
        font-weight: 500;
    }
    .stSelectbox > div > div:hover {
        border-color: #6B73FF;
    }
    
    /* 파일 업로더 */
    section[data-testid="stFileUploadDropzone"] {
        background: rgba(107, 115, 255, 0.05);
        border: 2px dashed rgba(107, 115, 255, 0.3);
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        background: rgba(107, 115, 255, 0.1);
        border-color: #6B73FF;
    }
    
    /* 데이터프레임 */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(107, 115, 255, 0.2);
    }
    
    /* 텍스트 입력 레이블 */
    .stTextInput > label {
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(107, 115, 255, 0.05);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(107, 115, 255, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(107, 115, 255, 0.5);
    }
    
    /* 컨테이너 패딩 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 안내 텍스트 */
    .stMarkdown {
        line-height: 1.6;
    }
    
    /* 키워드 입력 레이볻 */
    .search-input-container {
        position: relative;
    }
    
    /* 성공/에러 메시지 아이콘 */
    .stSuccess, .stError, .stWarning, .stInfo {
        padding: 16px;
        border-radius: 12px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# 사용자 로그 파일 경로
LOG_FILE = "api_usage_logs.json"

def hash_api_key(api_key):
    """API 키를 해시화하여 저장"""
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]

def load_user_logs():
    """API 키별 사용 로그 불러오기"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_logs(logs):
    """API 키별 사용 로그 저장하기"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def check_daily_limit(client_id, limit=25000):
    """일일 API 사용 한도 체크 (API 키 기준)"""
    hashed_id = hash_api_key(client_id)
    logs = load_user_logs()
    today = str(date.today())
    
    if hashed_id not in logs:
        logs[hashed_id] = {}
    
    if today not in logs[hashed_id]:
        logs[hashed_id][today] = 0
    
    return logs[hashed_id][today] < limit, logs[hashed_id][today]

def update_usage_count(client_id, count):
    """API 사용 횟수 업데이트 (API 키 기준)"""
    hashed_id = hash_api_key(client_id)
    logs = load_user_logs()
    today = str(date.today())
    
    if hashed_id not in logs:
        logs[hashed_id] = {}
    
    if today not in logs[hashed_id]:
        logs[hashed_id][today] = 0
    
    logs[hashed_id][today] += count
    save_user_logs(logs)

def search_naver_webkr(query, client_id, client_secret, display=10):
    """네이버 통합검색 API"""
    url = "https://openapi.naver.com/v1/search/webkr.xml"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": query,
        "display": display,
        "start": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            return "AUTH_ERROR"
        elif response.status_code == 429:
            return "RATE_LIMIT"
        elif response.status_code == 400:
            return "BAD_REQUEST"
        elif response.status_code == 500:
            return "SERVER_ERROR"
        else:
            return None
    except Exception as e:
        return None

def search_naver_shopping(query, client_id, client_secret, display=20):
    """네이버 쇼핑 API 검색"""
    url = "https://openapi.naver.com/v1/search/shop.xml"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": "sim"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            return "AUTH_ERROR"
        elif response.status_code == 429:
            return "RATE_LIMIT"
        elif response.status_code == 400:
            return "BAD_REQUEST"
        elif response.status_code == 500:
            return "SERVER_ERROR"
        else:
            return None
    except Exception as e:
        return None

def parse_webkr_xml(xml_text):
    """통합검색 XML 응답 파싱"""
    try:
        root = ET.fromstring(xml_text)
        records = []
        for item in root.findall('.//item'):
            records.append({
                "title": item.findtext('title', '').replace('<b>', '').replace('</b>', ''),
                "link": item.findtext('link', ''),
                "description": item.findtext('description', '').replace('<b>', '').replace('</b>', '')
            })
        return records
    except ET.ParseError:
        return []

def parse_shopping_xml(xml_text):
    """쇼핑검색 XML 응답 파싱 - 모든 필드 포함"""
    try:
        root = ET.fromstring(xml_text)
        records = []
        for item in root.findall('.//item'):
            records.append({
                "title": item.findtext('title', '').replace('<b>', '').replace('</b>', ''),
                "link": item.findtext('link', ''),
                "image": item.findtext('image', ''),
                "lprice": item.findtext('lprice', ''),
                "hprice": item.findtext('hprice', ''),
                "mallName": item.findtext('mallName', ''),
                "productId": item.findtext('productId', ''),
                "productType": item.findtext('productType', ''),
                "brand": item.findtext('brand', ''),
                "maker": item.findtext('maker', ''),
                "category1": item.findtext('category1', ''),
                "category2": item.findtext('category2', ''),
                "category3": item.findtext('category3', ''),
                "category4": item.findtext('category4', '')
            })
        return records
    except ET.ParseError:
        return []

def analyze_organic_rankings(webkr_records, shopping_records, target_domain=None):
    """오가닉 순위 분석 - 쇼핑검색은 광고/오가닉 구분 없이 전체 표시"""
    results = {
        'webkr_organic_start': None,
        'webkr_organic_positions': [],
        'shopping_positions': [],  # 쇼핑은 전체 포지션 추적
        'webkr_total': len(webkr_records),
        'shopping_total': len(shopping_records)
    }
    
    # 통합검색 오가닉 분석 (광고는 최대 4개)
    for i, record in enumerate(webkr_records[:10]):
        if i >= 4:  # 5번째부터는 확실히 오가닉
            if results['webkr_organic_start'] is None:
                results['webkr_organic_start'] = i + 1
            if target_domain and target_domain in record.get('link', ''):
                results['webkr_organic_positions'].append(i + 1)
    
    # 쇼핑검색 - 전체 결과 추적 (광고/오가닉 구분 없음)
    for i, record in enumerate(shopping_records):
        if target_domain and target_domain in record.get('mallName', ''):
            results['shopping_positions'].append(i + 1)
    
    return results

# 메인 앱
def main():
    st.markdown("""
    <h1 style='text-align: center; background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
    font-size: 3.5em; margin-bottom: 10px; font-weight: 800;'>
    네이버 쇼핑 키워드 분석기
    </h1>
    <p style='text-align: center; font-size: 1.2em; opacity: 0.7; margin-bottom: 40px;'>
    🔍 실시간 키워드 분석과 상품 정보 수집
    </p>
    """, unsafe_allow_html=True)
    
    # 사이드바 - API 설정
    with st.sidebar:
        st.markdown("<h2 style='color: white; text-align: center; margin-bottom: 30px; font-weight: 700;'>⚙️ API 설정</h2>", unsafe_allow_html=True)
        
        if 'client_id' not in st.session_state:
            st.session_state.client_id = ""
        if 'client_secret' not in st.session_state:
            st.session_state.client_secret = ""
        
        client_id = st.text_input(
            "네이버 클라이언트 ID", 
            type="password",
            value=st.session_state.client_id,
            key="client_id_input",
            placeholder="클라이언트 ID를 입력하세요"
        )
        client_secret = st.text_input(
            "네이버 클라이언트 시크릿", 
            type="password",
            value=st.session_state.client_secret,
            key="client_secret_input",
            placeholder="클라이언트 시크릿을 입력하세요"
        )
        
        if client_id:
            st.session_state.client_id = client_id
        if client_secret:
            st.session_state.client_secret = client_secret
        
        if client_id:
            can_use, today_usage = check_daily_limit(client_id)
            
            if not can_use:
                st.error("⚠️ 오늘 사용 한도를 초과했습니다!")
    
    # 메인 컨텐츠
    tab1, tab2 = st.tabs(["🔍 키워드 분석", "📊 일괄 검색"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<h3 style='margin-bottom: 25px; font-weight: 600;'>🎯 검색 설정</h3>", unsafe_allow_html=True)
            keyword = st.text_input("분석할 키워드:", placeholder="예: 운동화, 런닝화, 스니커즈...")
        
        with col2:
            if st.button("🔍 분석 시작", disabled=not (client_id and client_secret and keyword)):
                results = {}
                
                # 쇼핑검색
                shopping_xml = search_naver_shopping(keyword, client_id, client_secret)
                if shopping_xml == "AUTH_ERROR":
                    st.error("❌ API 키를 확인해주세요. 또는 네이버 개발자 센터에서 할당량을 확인해주세요!")
                    return
                elif shopping_xml == "RATE_LIMIT":
                    st.error("⏰ API 사용 한도를 초과했습니다. 네이버 개발자 센터에서 할당량을 확인해주세요!")
                    return
                elif shopping_xml == "BAD_REQUEST":
                    st.error("❌ 잘못된 요청입니다. 검색어나 파라미터를 확인해주세요.")
                    return
                elif shopping_xml == "SERVER_ERROR":
                    st.error("⚠️ 네이버 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                    return
                elif shopping_xml:
                    shopping_records = parse_shopping_xml(shopping_xml)
                    results['shopping'] = shopping_records
                    # 사용량 업데이트
                    update_usage_count(client_id, 1)
                else:
                    st.error("❌ 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                    return
                
                # 결과 분석
                if results and 'shopping' in results:
                    if len(results['shopping']) == 0:
                        st.warning("🔍 검색 결과가 없습니다.")
                    else:
                        st.markdown("<h3 style='margin: 30px 0 25px 0; font-weight: 600;'>📊 검색 결과</h3>", unsafe_allow_html=True)
                        st.markdown(f"<div class='metric-card' style='text-align: center;'><h3>{len(results['shopping'])}</h3><p>개의 상품을 찾았습니다</p></div>", unsafe_allow_html=True)
                        
                        # 결과를 카드 형태로 표시
                        for i, item in enumerate(results['shopping'][:20]):
                            price = f"{int(item['lprice']):,}원" if item['lprice'] else "가격정보 없음"
                            brand_info = f" | 브랜드: {item['brand']}" if item.get('brand') else ""
                            maker_info = f" | 제조사: {item['maker']}" if item.get('maker') else ""
                            category = f"{item.get('category1', '')} > {item.get('category2', '')}" if item.get('category1') else ""
                            
                            # 카드 스타일로 표시
                            st.markdown(f"""
                            <div class='result-card'>
                                <h4>{i+1}. {item['title']}</h4>
                                <p>🏪 <strong>{item['mallName']}</strong>{brand_info}{maker_info}</p>
                                <p>💰 <strong style='color: #6B73FF; font-size: 1.1em;'>{price}</strong></p>
                                <p>📂 {category}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<h3 style='margin-bottom: 25px; font-weight: 600;'>📝 일괄 키워드 분석</h3>", unsafe_allow_html=True)
        
        # 예시 파일 다운로드 기능
        col1, col2 = st.columns([1, 3])
        with col1:
            # 예시 파일 생성
            example_df = pd.DataFrame({
                '키워드': ['운동화', '런닝화', '나이키 운동화', '아디다스 신발', '스니커즈']
            })
            example_excel = BytesIO()
            with pd.ExcelWriter(example_excel, engine='openpyxl') as writer:
                example_df.to_excel(writer, index=False, sheet_name='키워드목록')
            example_excel.seek(0)
            
            st.download_button(
                label="📥 예시 파일 다운로드",
                data=example_excel,
                file_name="keyword_example.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # 파일 업로드
        uploaded_file = st.file_uploader(
            "엑셀 파일 업로드 (.xlsx, .xls)",
            type=['xlsx', 'xls'],
            help="최대 1,000개의 키워드까지 처리 가능합니다."
        )
        
        keywords = []
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                
                # 파일 로드 전 행 수 체크
                if len(df) > 1000:
                    st.error(f"❌ 파일에 {len(df):,}개의 행이 있습니다. 최대 1,000개까지만 받을 수 있습니다.")
                    st.stop()
                
                if len(df.columns) > 1:
                    keyword_col = st.selectbox(
                        "키워드 컬럼 선택:",
                        options=df.columns.tolist()
                    )
                else:
                    keyword_col = df.columns[0]
                
                keywords = df[keyword_col].dropna().astype(str).tolist()
                
                # 1000개 제한 (빈 값 제거 후 재확인)
                if len(keywords) > 1000:
                    st.error(f"❌ 유효한 키워드가 {len(keywords):,}개 있습니다. 최대 1,000개까지만 받을 수 있습니다.")
                    st.stop()
                
                st.success(f"✅ {len(keywords)}개 키워드 로드됨")
            except Exception as e:
                st.error(f"파일 읽기 오류: {str(e)}")
        
        if keywords:
            display_count = st.number_input("검색 결과 개수 (최대 100)", min_value=10, max_value=100, value=20, step=10)
            
            # 예상 사용량 계산
            expected_usage = len(keywords)
            can_use, today_usage = check_daily_limit(client_id) if client_id else (True, 0)
            remaining = 25000 - today_usage
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='metric-card'>📊 예상 API 호출: {expected_usage:,}회</div>", unsafe_allow_html=True)
            with col2:
                if expected_usage > remaining:
                    st.error(f"⚠️ 남은 한도({remaining:,})를 초과합니다!")
                
            if st.button("🚀 일괄 분석 시작", disabled=not (client_id and client_secret and keywords)):
                if expected_usage > remaining:
                    st.error("API 한도 초과로 실행할 수 없습니다!")
                    return
                
                progress_bar = st.progress(0)
                status_container = st.container()
                
                with status_container:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        status_text = st.empty()
                    with col2:
                        completed_text = st.empty()
                    with col3:
                        remaining_text = st.empty()
                
                all_results = []
                
                for i, keyword in enumerate(keywords):
                    current_progress = (i + 1) / len(keywords)
                    
                    # 상태 업데이트
                    status_text.text(f"🔍 분석 중: {keyword}")
                    completed_text.text(f"✅ 완료: {i+1}개")
                    remaining_text.text(f"⏳ 남음: {len(keywords) - i - 1}개")
                    
                    # 쇼핑검색
                    shopping_xml = search_naver_shopping(keyword, client_id, client_secret, display=display_count)
                    if shopping_xml == "AUTH_ERROR":
                        st.error("❌ API 키를 확인해주세요. 또는 네이버 개발자 센터에서 할당량을 확인해주세요!")
                        return
                    elif shopping_xml == "RATE_LIMIT":
                        st.error("⏰ API 사용 한도를 초과했습니다. 네이버 개발자 센터에서 할당량을 확인해주세요!")
                        return
                    elif shopping_xml == "BAD_REQUEST":
                        st.error("❌ 잘못된 요청입니다. 검색어나 파라미터를 확인해주세요.")
                        return
                    elif shopping_xml == "SERVER_ERROR":
                        st.error("⚠️ 네이버 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                        return
                    elif shopping_xml:
                        shopping_records = parse_shopping_xml(shopping_xml)
                        
                        # 각 상품별로 row 생성 - 모든 필드 포함
                        for idx, item in enumerate(shopping_records):
                            all_results.append({
                                'keyword': keyword,
                                'rank': idx + 1,
                                'title': item['title'],
                                'link': item['link'],
                                'image': item['image'],
                                'lprice': int(item['lprice']) if item['lprice'] else 0,
                                'hprice': int(item['hprice']) if item['hprice'] else 0,
                                'mall': item['mallName'],
                                'productId': item['productId'],
                                'productType': item['productType'],
                                'brand': item['brand'] or '',
                                'maker': item['maker'] or '',
                                'category1': item['category1'] or '',
                                'category2': item['category2'] or '',
                                'category3': item['category3'] or '',
                                'category4': item['category4'] or ''
                            })
                    
                    progress_bar.progress(current_progress)
                    time.sleep(0.1)  # API 호출 간격
                
                # 사용량 업데이트
                update_usage_count(client_id, expected_usage)
                
                # 완료 메시지
                status_text.text("✨ 분석 완료!")
                completed_text.text(f"✅ 완료: {len(keywords)}개")
                remaining_text.text("⏳ 남음: 0개")
                
                # 결과 표시
                if all_results:
                    result_df = pd.DataFrame(all_results)
                    
                    # 결과 요약
                    st.markdown("<h3 style='margin: 30px 0 25px 0; font-weight: 600;'>📊 분석 결과</h3>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"<div class='metric-card'><h3>{len(keywords):,}</h3><p>총 키워드</p></div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<div class='metric-card'><h3>{len(all_results):,}</h3><p>총 검색 결과</p></div>", unsafe_allow_html=True)
                    with col3:
                        if 'mall' in result_df.columns:
                            unique_malls = result_df['mall'].nunique()
                            st.markdown(f"<div class='metric-card'><h3>{unique_malls:,}</h3><p>쇼핑몰 수</p></div>", unsafe_allow_html=True)
                else:
                    st.warning("🔍 검색 결과가 없습니다.")
                    
                    # 전체 데이터 표시
                    st.markdown("<h3 style='margin: 30px 0 25px 0; font-weight: 600;'>🗂️ 전체 검색 결과</h3>", unsafe_allow_html=True)
                    st.dataframe(result_df, use_container_width=True, height=600)
                    
                    # 엑셀 다운로드
                    def convert_df_to_excel(df):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # 컬럼명 한글화
                            df_korean = df.rename(columns={
                                'keyword': '검색키워드',
                                'rank': '순위',
                                'title': '상품명',
                                'link': '상품링크',
                                'image': '이미지URL',
                                'lprice': '최저가',
                                'hprice': '최고가',
                                'mall': '쇼핑몰',
                                'productId': '상품ID',
                                'productType': '상품타입',
                                'brand': '브랜드',
                                'maker': '제조사',
                                'category1': '대분류',
                                'category2': '중분류',
                                'category3': '소분류',
                                'category4': '세분류'
                            })
                            df_korean.to_excel(writer, index=False, sheet_name='전체_검색결과')
                        
                        return output.getvalue()
                    
                    excel_data = convert_df_to_excel(result_df)
                    st.download_button(
                        label="📥 결과 다운로드 (Excel)",
                        data=excel_data,
                        file_name=f"naver_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    # 사용 가이드
    with st.expander("📖 사용 가이드"):
        st.markdown("""
        ### 🎯 네이버 쇼핑 키워드 분석기
        네이버 쇼핑 검색 결과를 분석하여 상품 정보를 수집합니다.
        
        ### 📝 일괄 분석 사용 방법
        1. **예시 파일 다운로드**: 키워드 입력 형식 확인
        2. **엑셀 파일 준비**: 키워드를 엑셀 파일에 입력 (최대 1,000개)
        3. **파일 업로드**: 준비한 엑셀 파일 업로드
        4. **분석 시작**: 검색 결과 개수 설정 후 분석 시작
        5. **결과 다운로드**: 분석 완료 후 엑셀 파일로 다운로드
        
        ### 📊 수집 데이터
        - 상품명, 링크, 이미지 URL
        - 최저가, 최고가, 쇼핑몰명
        - 상품 ID, 상품 타입
        - 브랜드, 제조사
        - 카테고리 정보 (대/중/소/세분류)
        
        ### ⚠️ 주의사항
        - 일일 최대 25,000회 API 호출 제한
        - 한 번에 최대 1,000개 키워드 처리 가능
        - 키워드당 최대 100개 상품 검색 가능
        """)

if __name__ == "__main__":
    main()