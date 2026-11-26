# seoulbikedashboard
객체지향프로그래밍

## 프로젝트 소개
서울시 공공자전거(따릉이) 대여소별 실시간 잔여 자전거 수와 혼잡도를 확인하고 비교할 수 있는 Streamlit 대시보드입니다.

서울열린데이터광장의 따릉이 실시간 대여정보 Open API를 불러와서 대여소별 현황을 정리하고, 자전거 수급이 몰리는 대여소를 검색·필터·지도·차트로 한눈에 볼 수 있게 만들었습니다. 

## 데이터 및 혼잡도 기준
데이터 출처: 서울열린데이터광장 — 서울시 공공자전거 실시간 대여정보 Open API

혼잡도 분류<br>
부족: 대여가능률 20% 미만<br>
보통: 대여가능률 20% 이상 ~ 60% 미만<br>
여유: 대여가능률 60% 이상<br>

## 구조 및 클래스 역할
역할이 한 곳에 뭉치지 않도록 모듈과 클래스를 나눠서 구성했습니다.

DataFetcher: Open API 요청과 원천 JSON 데이터 수집 <br>
DataProcessor: JSON을 pandas.DataFrame으로 바꾸고, 결측치 정리 및 대여율·혼잡도 계산 수행<br>
StationFilter: 대여소 이름 검색, 혼잡도 선택, 최소 자전거 수 등 사이드바 조건에 따른 연쇄 필터링<br>
DashboardUI: KPI 지표, Folium 지도 마커, 차트, 표 등 Streamlit 화면 요소 렌더링<br>

데이터는 DataFetcher → DataProcessor → StationFilter → DashboardUI 순서로 전달

## 주요 기능
요약 지표(KPI): 전체 대여소 수, 이용 가능 자전거 수, 총 거치대 수, 평균 대여가능률<br>
지도 시각화: Folium 기반 대여소 위치 및 혼잡도 상태 표시<br>
차트 및 데이터 표: 잔여 자전거 부족 대여소 차트, 혼잡도 비율 차트, 필터링된 목록 테이블<br>
조건 필터링: 대여소명 검색, 혼잡도 상태 선택(부족/보통/여유), 최소 자전거 수 슬라이더, 자전거 거치대 슬라이더, 데이터 새로고침, 서울 주요 권역 선택<br>

## 실행 방법
필요 환경<br>
Python 3.10 이상 환경에서 아래 라이브러리를 사용합니다.<br>
streamlit, pandas, folium, plotly, requests, python-dotenv<br>
pip install -r requirements.txt<br>

대시보드 실행<br>
streamlit run app.py<br>
GitHub 저장소와 연결해 Streamlit Community Cloud로 배포<br>
현재 url: https://seoulbikedashboard-test.streamlit.app/
