# 네이버 오가닉 키워드 분석기

네이버 검색결과에서 광고를 제외한 오가닉(자연) 검색 순위를 분석하는 도구입니다.

## 주요 기능

### 1. 통합검색 & 쇼핑검색 지원
- 네이버 통합검색 (웹검색) 분석
- 네이버 쇼핑검색 분석
- 각 검색별 광고/오가닉 구분

### 2. 네이버 광고 노출 규칙
- **통합검색**: 최대 4개 광고 (PC/모바일 동일)
- **쇼핑검색**: PC 최대 5개, 모바일 최대 4개 광고
- 광고 이후 순위부터 오가닉(자연) 검색결과로 분류

### 3. API 사용량 관리
- 일일 25,000회 제한 자동 관리
- API 키별 사용량 추적 (해시화 저장)
- 실시간 사용량 모니터링

### 4. 보안 기능
- API 키 해시화 저장
- 환경변수 지원
- Streamlit Secrets 연동

## 설치 방법

```bash
# 저장소 클론
git clone https://github.com/yourusername/OrganicKeyword.git
cd OrganicKeyword

# 필요 패키지 설치
pip install -r requirements.txt
```

## 사용 방법

### 1. API 키 설정

#### 방법 1: 직접 입력
- 앱 실행 후 사이드바에서 API 키 입력

#### 방법 2: 환경변수 사용 (권장)
```bash
# .env 파일 생성
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

#### 방법 3: Streamlit Cloud 배포시
```toml
# .streamlit/secrets.toml
NAVER_CLIENT_ID = "your_client_id"
NAVER_CLIENT_SECRET = "your_client_secret"
```

### 2. 앱 실행

```bash
streamlit run main.py
```

## 주요 기능 설명

### 키워드 분석
- 단일 키워드의 통합검색/쇼핑검색 결과 분석
- 광고 구간과 오가닉 구간 구분
- 특정 도메인/쇼핑몰의 오가닉 순위 확인

### 일괄 분석
- 다수 키워드 동시 분석
- 엑셀 파일 업로드 지원
- 결과 엑셀 다운로드

## 보안 주의사항

### Git 배포시
- API 키를 코드에 직접 입력하지 마세요
- `.env` 파일은 `.gitignore`에 추가
- 환경변수 또는 Secrets 사용 권장

### API 사용량
- 일일 25,000회 제한
- API 키는 해시화되어 로그에 저장
- 사용량 초과시 자동 차단

## 파일 구조

```
OrganicKeyword/
├── main.py                 # 메인 애플리케이션
├── api_usage_logs.json    # API 사용 로그 (자동 생성)
├── requirements.txt       # 필요 패키지 목록
├── .env                  # 환경변수 (로컬용, git 제외)
├── .gitignore           # Git 제외 파일
└── README.md           # 이 파일
```

## 요구사항

- Python 3.7+
- Streamlit
- pandas
- requests
- openpyxl

## 라이선스

MIT License

## 문의사항

문제가 있거나 기능 요청이 있으시면 Issues를 통해 알려주세요.