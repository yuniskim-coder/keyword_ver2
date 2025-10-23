# chaechaeLab 마케팅 도구

네이버 기반 종합 마케팅 분석 도구입니다.

## 🚀 기능

- **🎯 순위 확인기**: 네이버 쇼핑에서 특정 판매처의 상품 순위 확인
- **🔗 연관 키워드**: 키워드 연관성 분석 및 인사이트 제공
- **🛍️ 쇼핑 랭킹**: 네이버 쇼핑 인기 상품 순위 (개발 예정)
- **📈 월간 검색량**: 키워드별 월간 검색 트렌드 (개발 예정)

## 📁 프로젝트 구조

```
keyword_ver2/
├── app.py                 # 메인 애플리케이션
├── config.py             # 설정 파일
├── requirements.txt      # 패키지 의존성
├── modules/             # 핵심 모듈
│   ├── auth.py          # 인증 관련
│   └── __init__.py
├── pages/               # 페이지 모듈
│   ├── login.py         # 로그인 페이지
│   ├── rank_checker.py  # 순위 확인
│   ├── related_keywords.py # 연관 키워드
│   └── __init__.py
├── utils/               # 유틸리티
│   ├── naver_api.py     # 네이버 API
│   ├── styles.py        # UI 스타일
│   └── __init__.py
└── logo.ico             # 로고 파일
```

## 🔧 설치 및 실행

1. 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 애플리케이션 실행:
```bash
streamlit run app.py
```

## 🔑 로그인 정보

- **사용자 ID**: master
- **비밀번호**: 56tyghbn

## 📝 라이선스

Copyright ⓒ 2025 chaechaeLab. All rights reserved.
무단 복제 및 배포 금지.
