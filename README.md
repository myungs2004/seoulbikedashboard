# seoulbikedashboard
> 객체지향프로그래밍 팀 프로젝트

서울시 공공자전거(따릉이) 대여소의 잔여 자전거 수와 혼잡도를 확인하고 비교할 수 있는 Streamlit 대시보드입니다.

서울열린데이터광장의 따릉이 실시간 대여정보 Open API를 불러와서 대여소별 현황을 정리하고, 자전거 수급이 몰리는 대여소를 검색·필터·지도·차트로 한눈에 볼 수 있습니다.

## 데이터 및 혼잡도 기준
서울열린데이터광장의 [공공자전거 실시간 대여정보 Open API](https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do)를 사용합니다.

**대여 가능률(%)** = (잔여 자전거 수 ÷ 거치대 수) × 100

| 상태 | 대여 가능률 |
| --- | --- |
| 부족 | 20% 미만 |
| 보통 | 20% 이상 60% 미만 |
| 여유 | 60% 이상 |

## 구조 및 클래스 역할
역할이 한 곳에 뭉치지 않도록 모듈과 클래스를 나눠서 구성했습니다.

| 클래스 | 역할 |
| --- | --- |
| `DataFetcher` | 서울시 Open API를 호출해 대여소 원본 JSON을 수집 |
| `DataProcessor` | JSON을 pandas DataFrame으로 변환, 수량을 정제하여 대여 가능률과 상태를 계산 |
| `StationFilter` | 대여소 이름, 상태, 최소 잔여 자전거 수 조건을 차례대로 적용 |
| `DashboardUI` | KPI 지표, Folium 지도 마커, 차트, 표 등 Streamlit 화면 요소 렌더링 |

데이터는 `DataFetcher` → `DataProcessor` → `StationFilter` → `DashboardUI` 순서로 전달

## 주요 기능
- **요약 지표(KPI)** — 전체 대여소 수, 이용 가능 자전거 수, 총 거치대 수, 평균 대여가능률 표시
- **지도 시각화** — Folium 기반 대여소 위치 및 혼잡도 상태 표시
- **차트 및 데이터 표** — 잔여 자전거 부족 대여소 차트, 혼잡도 비율 차트, 필터링된 목록 테이블 표시
- **조건 필터링** — 대여소명 검색, 혼잡도 상태 선택(부족/보통/여유), 최소 자전거 수 슬라이더, 자전거 거치대 슬라이더, 데이터 새로고침, 서울 주요 권역 선택

## 실행 방법

### 필요 환경

- Python 3.10 이상
- 주요 라이브러리 — Streamlit, pandas, Folium, Plotly, Requests, python-dotenv

아래 명령으로 라이브러리를 설치합니다.

```sh
pip install -r requirements.txt
```

### 대시보드 실행

```sh
streamlit run app.py
```

### 배포

GitHub 저장소를 Streamlit Community Cloud에 연결해 테스트 버전을 배포했습니다.

[대시보드 열기](https://seoulbikedashboard-test.streamlit.app/)
